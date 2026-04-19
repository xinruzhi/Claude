#!/usr/bin/env python3
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path
from typing import Optional

from backend.models.resume import Resume
from backend.core.resume_parser import ResumeParser
from backend.core.version_manager import VersionManager
from backend.agents.content_optimizer import ContentOptimizer
from backend.agents.job_matcher import JobMatcher
from backend.agents.template_generator import TemplateGenerator
from backend.utils.pdf_generator import PDFGenerator

app = typer.Typer(
    name="resume-optimizer",
    help="智能简历优化工具 - Resume Optimizer",
    add_completion=False
)

console = Console()
parser = ResumeParser()
version_manager = VersionManager()
optimizer = ContentOptimizer()
matcher = JobMatcher()
template_generator = TemplateGenerator()
pdf_generator = PDFGenerator()


@app.command()
def parse(
    file_path: str = typer.Argument(..., help="简历文件路径"),
    save: bool = typer.Option(True, help="是否保存解析结果")
):
    """解析简历文件"""
    file = Path(file_path)
    if not file.exists():
        console.print(f"[red]错误：文件不存在[/red] {file_path}")
        raise typer.Exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("解析简历中...", total=None)
        try:
            resume = parser.parse_file(file_path)
            progress.update(task, completed=True)
        except Exception as e:
            console.print(f"[red]解析失败：[/red] {str(e)}")
            raise typer.Exit(1)

    if resume:
        console.print("\n[green]✓ 简历解析成功！[/green]\n")

        table = Table(show_header=False, box=None)
        table.add_row("姓名", resume.name)
        table.add_row("职位", resume.title)
        table.add_row("邮箱", resume.email)
        table.add_row("技能数", str(len(resume.skills)))
        table.add_row("工作经历", str(len(resume.experience)))
        console.print(table)

        if save:
            resume_id = version_manager.save_version(resume, "Parsed from CLI")
            console.print(f"\n[blue]简历已保存，ID:[/blue] {resume_id}")
            return resume_id
    else:
        console.print("[yellow]未能解析简历内容[/yellow]")


@app.command()
def optimize(
    resume_id: str = typer.Argument(..., help="简历ID"),
    role: Optional[str] = typer.Option(None, "--role", "-r", help="目标职位"),
    industry: Optional[str] = typer.Option(None, "--industry", "-i", help="行业"),
    note: str = typer.Option("Optimized", "--note", "-n", help="版本说明")
):
    """优化简历"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("获取简历...", total=None)
        resume = version_manager.get_version(resume_id, "latest")

        if not resume:
            console.print(f"[red]错误：找不到简历[/red] {resume_id}")
            raise typer.Exit(1)

        progress.update(task, description="优化中...")
        result = optimizer.optimize_resume(resume, role, industry)
        progress.update(task, completed=True)

    console.print("\n[green]✓ 优化完成！[/green]\n")

    console.print(f"ATS 评分：{result.ats_score:.1f}/100")

    if result.suggestions:
        console.print("\n[bold]优化建议：[/bold]")
        for i, suggestion in enumerate(result.suggestions[:5], 1):
            console.print(f"  {i}. {suggestion}")

    new_id = version_manager.save_version(result.optimized_resume, note)
    console.print(f"\n[blue]新版本已保存，ID:[/blue] {new_id}")


@app.command()
def match(
    resume_id: str = typer.Argument(..., help="简历ID"),
    job_file: str = typer.Argument(..., help="职位描述文件"),
    company: Optional[str] = typer.Option(None, "--company", "-c", help="公司名称")
):
    """匹配简历与职位"""
    from backend.models.job_description import JobDescription

    job_file_path = Path(job_file)
    if not job_file_path.exists():
        console.print(f"[red]错误：文件不存在[/red] {job_file}")
        raise typer.Exit(1)

    resume = version_manager.get_version(resume_id, "latest")
    if not resume:
        console.print(f"[red]错误：找不到简历[/red] {resume_id}")
        raise typer.Exit(1)

    with open(job_file_path, 'r', encoding='utf-8') as f:
        job_desc = f.read()

    job = JobDescription(
        title="Target Position",
        company=company or "Unknown",
        description=job_desc
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("分析匹配度...", total=None)
        result = matcher.match_resume_to_job(resume, job)
        progress.update(task, completed=True)

    console.print("\n[bold]匹配分析结果[/bold]\n")

    score_color = "green" if result.match_score >= 70 else "yellow" if result.match_score >= 50 else "red"
    console.print(f"总体匹配度：[{score_color}]{result.match_score:.0f}/100[/{score_color}]")

    table = Table(show_header=True)
    table.add_column("维度")
    table.add_column("分数", justify="right")
    table.add_row("技能匹配", f"{result.skill_match_score:.0f}")
    table.add_row("经验匹配", f"{result.experience_match_score:.0f}")
    table.add_row("关键词匹配", f"{result.keyword_match_score:.0f}")
    console.print(table)

    if result.missing_skills:
        console.print(f"\n[red]缺失技能：[/red] {', '.join(result.missing_skills[:5])}")

    if result.suggestions:
        console.print("\n[bold]改进建议：[/bold]")
        for i, suggestion in enumerate(result.suggestions[:3], 1):
            console.print(f"  {i}. {suggestion}")


@app.command()
def export(
    resume_id: str = typer.Argument(..., help="简历ID"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="输出文件路径"),
    style: str = typer.Option("modern", "--style", "-s", help="模板风格: modern, classic, minimalist"),
    format: str = typer.Option("pdf", "--format", "-f", help="格式: pdf, markdown")
):
    """导出简历"""
    resume = version_manager.get_version(resume_id, "latest")
    if not resume:
        console.print(f"[red]错误：找不到简历[/red] {resume_id}")
        raise typer.Exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"生成{format.upper()}...", total=None)

        if format == "pdf":
            output_path = pdf_generator.generate_pdf(resume, output, style)
        else:
            md = template_generator.generate_markdown(resume, style)
            output_path = output or f"{resume.name.replace(' ', '_')}.md"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md)

        progress.update(task, completed=True)

    console.print(f"\n[green]✓ 导出成功！[/green] {output_path}")


@app.command()
def list(resume_id: Optional[str] = typer.Argument(None, help="简历ID（可选）")):
    """列出简历版本"""
    if resume_id:
        versions = version_manager.list_versions(resume_id)
        if not versions:
            console.print("[yellow]没有找到版本[/yellow]")
            return

        console.print(f"\n[bold]简历 {resume_id} 的版本：[/bold]\n")
        table = Table()
        table.add_column("版本")
        table.add_column("说明")
        table.add_column("保存时间")
        for v in versions:
            table.add_row(v['version'], v['version_note'], v['saved_at'][:19])
        console.print(table)
    else:
        data_dir = Path("./data/resumes")
        if data_dir.exists():
            resumes = [d.name for d in data_dir.iterdir() if d.is_dir()]
            if resumes:
                console.print(f"\n[bold]找到 {len(resumes)} 个简历：[/bold]\n")
                for r in resumes:
                    console.print(f"  • {r}")
            else:
                console.print("[yellow]还没有保存的简历[/yellow]")
        else:
            console.print("[yellow]还没有保存的简历[/yellow]")


if __name__ == "__main__":
    app()
