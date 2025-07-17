# -*- coding: utf-8 -*-
"""
실시간 성능 모니터링 시스템
카페24 자동화 작업의 성능을 실시간으로 모니터링하고 분석
"""

import time
import json
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """실시간 성능 모니터링 시스템"""
    
    def __init__(self, monitoring_interval: float = 1.0):
        self.monitoring_interval = monitoring_interval
        self.is_monitoring = False
        self.monitor_thread = None
        
        # 성능 데이터 저장
        self.metrics_history = []
        self.operation_metrics = {}
        self.system_metrics = []
        
        # 임계값 설정
        self.thresholds = {
            'cpu_warning': 70,
            'cpu_critical': 85,
            'memory_warning': 75,
            'memory_critical': 90,
            'operation_timeout_warning': 10,
            'operation_timeout_critical': 20
        }
        
        # 알림 콜백
        self.alert_callbacks = []
    
    def start_monitoring(self):
        """모니터링 시작"""
        if self.is_monitoring:
            logger.warning("이미 모니터링이 실행 중입니다.")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("🔍 성능 모니터링 시작")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        logger.info("⏹️ 성능 모니터링 중지")
    
    def record_operation_start(self, operation_name: str, operation_id: str = None):
        """작업 시작 기록"""
        if not operation_id:
            operation_id = f"{operation_name}_{int(time.time())}"
        
        self.operation_metrics[operation_id] = {
            'name': operation_name,
            'start_time': time.time(),
            'end_time': None,
            'duration': None,
            'success': None,
            'memory_start': psutil.virtual_memory().percent,
            'cpu_start': psutil.cpu_percent(),
            'details': {}
        }
        
        logger.debug(f"📊 작업 시작 기록: {operation_name} (ID: {operation_id})")
        return operation_id
    
    def record_operation_end(self, operation_id: str, success: bool = True, details: Dict = None):
        """작업 종료 기록"""
        if operation_id not in self.operation_metrics:
            logger.warning(f"알 수 없는 작업 ID: {operation_id}")
            return
        
        operation = self.operation_metrics[operation_id]
        operation['end_time'] = time.time()
        operation['duration'] = operation['end_time'] - operation['start_time']
        operation['success'] = success
        operation['memory_end'] = psutil.virtual_memory().percent
        operation['cpu_end'] = psutil.cpu_percent()
        
        if details:
            operation['details'].update(details)
        
        # 성능 분석
        self._analyze_operation_performance(operation_id)
        
        logger.debug(f"📊 작업 종료 기록: {operation['name']} (소요시간: {operation['duration']:.2f}초)")
    
    def get_current_metrics(self) -> Dict:
        """현재 시스템 메트릭 반환"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metrics = {
                'timestamp': time.time(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024**3),
                'active_operations': len([op for op in self.operation_metrics.values() if op['end_time'] is None])
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"메트릭 수집 실패: {e}")
            return {}
    
    def get_performance_summary(self, hours: int = 1) -> Dict:
        """성능 요약 정보 반환"""
        cutoff_time = time.time() - (hours * 3600)
        
        # 최근 작업들 필터링
        recent_operations = [
            op for op in self.operation_metrics.values()
            if op['start_time'] >= cutoff_time and op['end_time'] is not None
        ]
        
        if not recent_operations:
            return {"message": f"최근 {hours}시간 동안 완료된 작업이 없습니다."}
        
        # 통계 계산
        total_operations = len(recent_operations)
        successful_operations = len([op for op in recent_operations if op['success']])
        success_rate = (successful_operations / total_operations) * 100
        
        durations = [op['duration'] for op in recent_operations]
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        min_duration = min(durations)
        
        # 작업별 통계
        operation_stats = {}
        for op in recent_operations:
            name = op['name']
            if name not in operation_stats:
                operation_stats[name] = {'count': 0, 'total_duration': 0, 'success_count': 0}
            
            operation_stats[name]['count'] += 1
            operation_stats[name]['total_duration'] += op['duration']
            if op['success']:
                operation_stats[name]['success_count'] += 1
        
        # 평균 계산
        for name, stats in operation_stats.items():
            stats['avg_duration'] = stats['total_duration'] / stats['count']
            stats['success_rate'] = (stats['success_count'] / stats['count']) * 100
        
        return {
            'period_hours': hours,
            'total_operations': total_operations,
            'success_rate': success_rate,
            'avg_duration': avg_duration,
            'max_duration': max_duration,
            'min_duration': min_duration,
            'operation_breakdown': operation_stats
        }
    
    def get_performance_alerts(self) -> List[Dict]:
        """성능 알림 목록 반환"""
        alerts = []
        current_metrics = self.get_current_metrics()
        
        if not current_metrics:
            return alerts
        
        # CPU 사용률 체크
        cpu_percent = current_metrics.get('cpu_percent', 0)
        if cpu_percent >= self.thresholds['cpu_critical']:
            alerts.append({
                'type': 'CRITICAL',
                'category': 'CPU',
                'message': f"CPU 사용률이 매우 높습니다: {cpu_percent:.1f}%",
                'value': cpu_percent,
                'threshold': self.thresholds['cpu_critical']
            })
        elif cpu_percent >= self.thresholds['cpu_warning']:
            alerts.append({
                'type': 'WARNING',
                'category': 'CPU',
                'message': f"CPU 사용률이 높습니다: {cpu_percent:.1f}%",
                'value': cpu_percent,
                'threshold': self.thresholds['cpu_warning']
            })
        
        # 메모리 사용률 체크
        memory_percent = current_metrics.get('memory_percent', 0)
        if memory_percent >= self.thresholds['memory_critical']:
            alerts.append({
                'type': 'CRITICAL',
                'category': 'MEMORY',
                'message': f"메모리 사용률이 매우 높습니다: {memory_percent:.1f}%",
                'value': memory_percent,
                'threshold': self.thresholds['memory_critical']
            })
        elif memory_percent >= self.thresholds['memory_warning']:
            alerts.append({
                'type': 'WARNING',
                'category': 'MEMORY',
                'message': f"메모리 사용률이 높습니다: {memory_percent:.1f}%",
                'value': memory_percent,
                'threshold': self.thresholds['memory_warning']
            })
        
        # 장시간 실행 작업 체크
        current_time = time.time()
        for op_id, op in self.operation_metrics.items():
            if op['end_time'] is None:  # 실행 중인 작업
                duration = current_time - op['start_time']
                if duration >= self.thresholds['operation_timeout_critical']:
                    alerts.append({
                        'type': 'CRITICAL',
                        'category': 'OPERATION',
                        'message': f"작업이 너무 오래 실행되고 있습니다: {op['name']} ({duration:.1f}초)",
                        'value': duration,
                        'threshold': self.thresholds['operation_timeout_critical'],
                        'operation_id': op_id
                    })
                elif duration >= self.thresholds['operation_timeout_warning']:
                    alerts.append({
                        'type': 'WARNING',
                        'category': 'OPERATION',
                        'message': f"작업 실행 시간이 깁니다: {op['name']} ({duration:.1f}초)",
                        'value': duration,
                        'threshold': self.thresholds['operation_timeout_warning'],
                        'operation_id': op_id
                    })
        
        return alerts
    
    def export_metrics(self, filename: str = None) -> str:
        """메트릭 데이터 내보내기"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_metrics_{timestamp}.json"
        
        export_data = {
            'export_timestamp': time.time(),
            'system_metrics': self.system_metrics[-1000:],  # 최근 1000개
            'operation_metrics': dict(self.operation_metrics),
            'thresholds': self.thresholds,
            'summary': self.get_performance_summary(24)  # 24시간 요약
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📁 성능 메트릭 내보내기 완료: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"메트릭 내보내기 실패: {e}")
            return None
    
    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.is_monitoring:
            try:
                metrics = self.get_current_metrics()
                if metrics:
                    self.system_metrics.append(metrics)
                    
                    # 최근 10000개 메트릭만 유지
                    if len(self.system_metrics) > 10000:
                        self.system_metrics = self.system_metrics[-10000:]
                    
                    # 알림 체크
                    alerts = self.get_performance_alerts()
                    for alert in alerts:
                        self._trigger_alert(alert)
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(self.monitoring_interval)
    
    def _analyze_operation_performance(self, operation_id: str):
        """작업 성능 분석"""
        operation = self.operation_metrics[operation_id]
        duration = operation['duration']
        name = operation['name']
        
        # 성능 임계값 체크
        if duration > self.thresholds['operation_timeout_critical']:
            logger.warning(f"⚠️ 작업 성능 경고: {name} - {duration:.2f}초 (임계값: {self.thresholds['operation_timeout_critical']}초)")
        
        # 메모리 사용량 변화 체크
        memory_change = operation.get('memory_end', 0) - operation.get('memory_start', 0)
        if memory_change > 10:  # 10% 이상 증가
            logger.warning(f"🧠 메모리 사용량 증가: {name} - {memory_change:.1f}%")
    
    def _trigger_alert(self, alert: Dict):
        """알림 트리거"""
        # 중복 알림 방지 (같은 카테고리의 알림이 최근 1분 내에 발생했는지 체크)
        current_time = time.time()
        recent_alerts = [
            m for m in self.system_metrics[-60:]  # 최근 60초
            if 'alerts' in m and any(
                a['category'] == alert['category'] and a['type'] == alert['type']
                for a in m.get('alerts', [])
            )
        ]
        
        if recent_alerts:
            return  # 중복 알림 방지
        
        # 알림 기록
        if self.system_metrics:
            if 'alerts' not in self.system_metrics[-1]:
                self.system_metrics[-1]['alerts'] = []
            self.system_metrics[-1]['alerts'].append(alert)
        
        # 콜백 실행
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"알림 콜백 실행 실패: {e}")
    
    def add_alert_callback(self, callback: callable):
        """알림 콜백 추가"""
        self.alert_callbacks.append(callback)
    
    def set_threshold(self, metric: str, value: float):
        """임계값 설정"""
        if metric in self.thresholds:
            self.thresholds[metric] = value
            logger.info(f"임계값 변경: {metric} = {value}")
        else:
            logger.warning(f"알 수 없는 메트릭: {metric}")

# 전역 모니터 인스턴스
global_monitor = PerformanceMonitor()

# 컨텍스트 매니저
class OperationMonitor:
    """작업 모니터링 컨텍스트 매니저"""
    
    def __init__(self, operation_name: str, monitor: PerformanceMonitor = None):
        self.operation_name = operation_name
        self.monitor = monitor or global_monitor
        self.operation_id = None
    
    def __enter__(self):
        self.operation_id = self.monitor.record_operation_start(self.operation_name)
        return self.operation_id
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        success = exc_type is None
        details = {}
        
        if exc_type:
            details['error_type'] = exc_type.__name__
            details['error_message'] = str(exc_val)
        
        self.monitor.record_operation_end(self.operation_id, success, details)