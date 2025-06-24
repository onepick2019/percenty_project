// 퍼센티 확장 프로그램 Background Service Worker
// Manifest V3 호환 버전

// Chrome Runtime API 안전 체크
if (typeof chrome !== 'undefined' && chrome.runtime) {
    console.log('퍼센티 확장 프로그램 Background Service Worker 시작');

    // 확장 프로그램 설치/업데이트 시 실행
    chrome.runtime.onInstalled.addListener((details) => {
        console.log('퍼센티 확장 프로그램 설치/업데이트:', details.reason);
        
        if (details.reason === 'install') {
            console.log('퍼센티 확장 프로그램이 처음 설치되었습니다.');
        } else if (details.reason === 'update') {
            console.log('퍼센티 확장 프로그램이 업데이트되었습니다.');
        }
    });

    // 메시지 리스너
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
        console.log('Background에서 메시지 수신:', request);
        
        try {
            // 메시지 타입에 따른 처리
            switch (request.type) {
                case 'GET_EXTENSION_INFO':
                    sendResponse({
                        success: true,
                        data: {
                            id: chrome.runtime.id,
                            version: chrome.runtime.getManifest().version,
                            name: chrome.runtime.getManifest().name
                        }
                    });
                    break;
                    
                case 'STORAGE_GET':
                    chrome.storage.local.get(request.keys, (result) => {
                        sendResponse({ success: true, data: result });
                    });
                    return true; // 비동기 응답을 위해 true 반환
                    
                case 'STORAGE_SET':
                    chrome.storage.local.set(request.data, () => {
                        sendResponse({ success: true });
                    });
                    return true; // 비동기 응답을 위해 true 반환
                    
                case 'GET_ACTIVE_TAB':
                    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
                        if (tabs.length > 0) {
                            sendResponse({ success: true, data: tabs[0] });
                        } else {
                            sendResponse({ success: false, error: '활성 탭을 찾을 수 없습니다.' });
                        }
                    });
                    return true; // 비동기 응답을 위해 true 반환
                    
                default:
                    console.log('알 수 없는 메시지 타입:', request.type);
                    sendResponse({ success: false, error: '알 수 없는 메시지 타입' });
            }
        } catch (error) {
            console.error('Background 메시지 처리 중 오류:', error);
            sendResponse({ success: false, error: error.message });
        }
    });

    // 탭 업데이트 리스너
    chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
        if (changeInfo.status === 'complete' && tab.url) {
            console.log('탭 업데이트 완료:', tab.url);
            
            // 퍼센티 사이트에서 확장 프로그램 상태 확인
            if (tab.url.includes('percenty.co.kr')) {
                console.log('퍼센티 사이트 감지됨');
                
                // 컨텐츠 스크립트에 메시지 전송
                chrome.tabs.sendMessage(tabId, {
                    type: 'EXTENSION_READY',
                    data: {
                        extensionId: chrome.runtime.id,
                        version: chrome.runtime.getManifest().version
                    }
                }).catch(error => {
                    console.log('컨텐츠 스크립트에 메시지 전송 실패:', error);
                });
            }
        }
    });

    // 컨텍스트 메뉴 생성 (선택사항)
    chrome.contextMenus.create({
        id: 'percenty-extension',
        title: '퍼센티로 상품 수집',
        contexts: ['page', 'selection']
    });

    // 컨텍스트 메뉴 클릭 리스너
    chrome.contextMenus.onClicked.addListener((info, tab) => {
        if (info.menuItemId === 'percenty-extension') {
            console.log('퍼센티 컨텍스트 메뉴 클릭됨');
            
            // 현재 탭에 메시지 전송
            chrome.tabs.sendMessage(tab.id, {
                type: 'CONTEXT_MENU_CLICKED',
                data: {
                    pageUrl: info.pageUrl,
                    selectionText: info.selectionText
                }
            }).catch(error => {
                console.log('컨텍스트 메뉴 메시지 전송 실패:', error);
            });
        }
    });

    // 확장 프로그램 아이콘 클릭 리스너
    chrome.action.onClicked.addListener((tab) => {
        console.log('확장 프로그램 아이콘 클릭됨:', tab.url);
    });

    // 웹 네비게이션 리스너
    chrome.webNavigation.onCompleted.addListener((details) => {
        if (details.frameId === 0) { // 메인 프레임만
            console.log('페이지 로딩 완료:', details.url);
        }
    });

    // 오류 처리
    chrome.runtime.onSuspend.addListener(() => {
        console.log('Background script 일시 중단됨');
    });

    chrome.runtime.onSuspendCanceled.addListener(() => {
        console.log('Background script 일시 중단 취소됨');
    });

} else {
    console.error('Chrome Runtime API를 사용할 수 없습니다.');
}

// 전역 오류 처리
self.addEventListener('error', (event) => {
    console.error('Background script 전역 오류:', event.error);
});

self.addEventListener('unhandledrejection', (event) => {
    console.error('Background script 처리되지 않은 Promise 거부:', event.reason);
});

console.log('퍼센티 Background Service Worker 초기화 완료');