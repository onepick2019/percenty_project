# -*- coding: utf-8 -*-
"""
자동 문서화 생성기
코드베이스를 분석하여 자동으로 문서를 생성합니다.
"""

import os
import ast
import inspect
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class CodeAnalyzer:
    """코드 분석기"""
    
    def __init__(self, project_root: str):
        """
        코드 분석기 초기화
        
        Args:
            project_root: 프로젝트 루트 디렉토리 경로
        """
        self.project_root = Path(project_root)
        self.analysis_results = {}
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Python 파일 분석
        
        Args:
            file_path: 분석할 파일 경로
            
        Returns:
            분석 결과 딕셔너리
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # AST 파싱
            tree = ast.parse(content)
            
            analysis = {
                'file_path': file_path,
                'classes': [],
                'functions': [],
                'imports': [],
                'docstring': ast.get_docstring(tree),
                'line_count': len(content.splitlines()),
                'complexity_score': self._calculate_complexity(tree)
            }
            
            # AST 노드 순회
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    analysis['classes'].append(self._analyze_class(node))
                elif isinstance(node, ast.FunctionDef):
                    analysis['functions'].append(self._analyze_function(node))
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    analysis['imports'].append(self._analyze_import(node))
            
            return analysis
            
        except Exception as e:
            logger.error(f"파일 분석 실패 {file_path}: {e}")
            return {'error': str(e), 'file_path': file_path}
    
    def _analyze_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        """클래스 분석"""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(self._analyze_function(item))
        
        return {
            'name': node.name,
            'docstring': ast.get_docstring(node),
            'methods': methods,
            'line_number': node.lineno,
            'base_classes': [base.id for base in node.bases if isinstance(base, ast.Name)]
        }
    
    def _analyze_function(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """함수 분석"""
        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        
        return {
            'name': node.name,
            'docstring': ast.get_docstring(node),
            'arguments': args,
            'line_number': node.lineno,
            'is_async': isinstance(node, ast.AsyncFunctionDef),
            'decorators': [dec.id for dec in node.decorator_list if isinstance(dec, ast.Name)]
        }
    
    def _analyze_import(self, node) -> Dict[str, Any]:
        """임포트 분석"""
        if isinstance(node, ast.Import):
            return {
                'type': 'import',
                'modules': [alias.name for alias in node.names]
            }
        elif isinstance(node, ast.ImportFrom):
            return {
                'type': 'from_import',
                'module': node.module,
                'names': [alias.name for alias in node.names]
            }
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """코드 복잡도 계산 (간단한 버전)"""
        complexity = 1  # 기본 복잡도
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def analyze_project(self) -> Dict[str, Any]:
        """전체 프로젝트 분석"""
        logger.info(f"프로젝트 분석 시작: {self.project_root}")
        
        python_files = list(self.project_root.rglob("*.py"))
        total_files = len(python_files)
        
        project_analysis = {
            'project_root': str(self.project_root),
            'total_files': total_files,
            'files': {},
            'summary': {
                'total_classes': 0,
                'total_functions': 0,
                'total_lines': 0,
                'average_complexity': 0
            }
        }
        
        total_complexity = 0
        
        for i, file_path in enumerate(python_files, 1):
            logger.info(f"분석 중 ({i}/{total_files}): {file_path.name}")
            
            relative_path = str(file_path.relative_to(self.project_root))
            analysis = self.analyze_file(str(file_path))
            
            if 'error' not in analysis:
                project_analysis['files'][relative_path] = analysis
                project_analysis['summary']['total_classes'] += len(analysis['classes'])
                project_analysis['summary']['total_functions'] += len(analysis['functions'])
                project_analysis['summary']['total_lines'] += analysis['line_count']
                total_complexity += analysis['complexity_score']
        
        # 평균 복잡도 계산
        if total_files > 0:
            project_analysis['summary']['average_complexity'] = total_complexity / total_files
        
        self.analysis_results = project_analysis
        logger.info("프로젝트 분석 완료")
        
        return project_analysis

class DocumentationGenerator:
    """문서 생성기"""
    
    def __init__(self, analysis_results: Dict[str, Any]):
        """
        문서 생성기 초기화
        
        Args:
            analysis_results: 코드 분석 결과
        """
        self.analysis_results = analysis_results
    
    def generate_markdown_docs(self, output_dir: str) -> None:
        """마크다운 문서 생성"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 프로젝트 개요 문서
        self._generate_project_overview(output_path)
        
        # 각 파일별 문서
        for file_path, analysis in self.analysis_results['files'].items():
            self._generate_file_documentation(output_path, file_path, analysis)
        
        logger.info(f"문서 생성 완료: {output_path}")
    
    def _generate_project_overview(self, output_path: Path) -> None:
        """프로젝트 개요 문서 생성"""
        summary = self.analysis_results['summary']
        
        content = f"""# 프로젝트 개요
        
## 통계
- 총 파일 수: {self.analysis_results['total_files']}
- 총 클래스 수: {summary['total_classes']}
- 총 함수 수: {summary['total_functions']}
- 총 라인 수: {summary['total_lines']:,}
- 평균 복잡도: {summary['average_complexity']:.2f}

## 파일 목록
"""
        
        for file_path in sorted(self.analysis_results['files'].keys()):
            content += f"- [{file_path}]({file_path.replace('/', '_').replace('.py', '.md')})\n"
        
        with open(output_path / "README.md", 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _generate_file_documentation(self, output_path: Path, file_path: str, analysis: Dict[str, Any]) -> None:
        """파일별 문서 생성"""
        filename = file_path.replace('/', '_').replace('.py', '.md')
        
        content = f"""# {file_path}

## 개요
- 라인 수: {analysis['line_count']}
- 복잡도: {analysis['complexity_score']}
- 클래스 수: {len(analysis['classes'])}
- 함수 수: {len(analysis['functions'])}

"""
        
        if analysis['docstring']:
            content += f"## 설명\n{analysis['docstring']}\n\n"
        
        # 클래스 문서화
        if analysis['classes']:
            content += "## 클래스\n\n"
            for cls in analysis['classes']:
                content += f"### {cls['name']}\n"
                if cls['docstring']:
                    content += f"{cls['docstring']}\n\n"
                
                if cls['methods']:
                    content += "#### 메서드\n"
                    for method in cls['methods']:
                        content += f"- `{method['name']}({', '.join(method['arguments'])})`"
                        if method['docstring']:
                            content += f": {method['docstring'].split('.')[0]}"
                        content += "\n"
                content += "\n"
        
        # 함수 문서화
        if analysis['functions']:
            content += "## 함수\n\n"
            for func in analysis['functions']:
                content += f"### {func['name']}\n"
                content += f"- 인수: `{', '.join(func['arguments'])}`\n"
                if func['docstring']:
                    content += f"- 설명: {func['docstring']}\n"
                content += "\n"
        
        with open(output_path / filename, 'w', encoding='utf-8') as f:
            f.write(content)

def generate_project_documentation(project_root: str, output_dir: str) -> None:
    """프로젝트 문서 자동 생성"""
    logger.info("프로젝트 문서 자동 생성 시작")
    
    # 코드 분석
    analyzer = CodeAnalyzer(project_root)
    analysis_results = analyzer.analyze_project()
    
    # 분석 결과 저장
    analysis_file = Path(output_dir) / "analysis_results.json"
    analysis_file.parent.mkdir(exist_ok=True)
    
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)
    
    # 문서 생성
    doc_generator = DocumentationGenerator(analysis_results)
    doc_generator.generate_markdown_docs(output_dir)
    
    logger.info("프로젝트 문서 자동 생성 완료")

if __name__ == "__main__":
    # 현재 프로젝트 문서화
    project_root = os.path.dirname(os.path.dirname(__file__))
    output_dir = os.path.join(project_root, "docs", "auto_generated")
    
    generate_project_documentation(project_root, output_dir)