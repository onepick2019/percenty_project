# -*- coding: utf-8 -*-
"""
성능 최적화 설정
카페24 테스트 결과 기반 성능 병목 지점 개선을 위한 설정
"""

class PerformanceConfig:
    """성능 최적화 관련 설정"""
    
    # 병목 지점별 최적화 설정
    TAB_CLEANUP_OPTIMIZATION = {
        'enabled': True,
        'max_wait_time': 10,  # 기존 18초에서 10초로 단축
        'force_close_timeout': 5,
        'parallel_cleanup': True
    }
    
    LOGIN_OPTIMIZATION = {
        'enabled': True,
        'cache_login_state': True,
        'skip_unnecessary_waits': True,
        'optimized_element_detection': True
    }
    
    PAGE_NAVIGATION_OPTIMIZATION = {
        'enabled': True,
        'preload_common_elements': True,
        'cache_page_state': True,
        'smart_wait_conditions': True
    }
    
    # 동적 대기 시간 설정
    ADAPTIVE_WAIT = {
        'enabled': True,
        'base_timeout': 5,
        'max_timeout': 15,
        'increment_factor': 1.5,
        'system_load_threshold': 0.8
    }
    
    # 리소스 사용량 모니터링
    RESOURCE_MONITORING = {
        'enabled': True,
        'memory_threshold_mb': 500,
        'cpu_threshold_percent': 80,
        'cleanup_interval_seconds': 300
    }

class OptimizationMetrics:
    """성능 메트릭 수집 설정"""
    
    COLLECT_METRICS = True
    METRICS_FILE = "performance_metrics.json"
    
    # 수집할 메트릭 종류
    METRICS_TO_COLLECT = [
        'step_execution_time',
        'memory_usage',
        'cpu_usage',
        'network_requests',
        'dom_operations',
        'javascript_execution_time'
    ]
    
    # 성능 임계값
    PERFORMANCE_THRESHOLDS = {
        'login_time': 8.0,  # 8초 이내
        'page_navigation': 6.0,  # 6초 이내
        'modal_processing': 2.0,  # 2초 이내
        'tab_cleanup': 8.0,  # 8초 이내
        'total_execution': 45.0  # 45초 이내
    }