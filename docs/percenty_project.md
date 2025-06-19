이번 프로젝트는 퍼센티 웹사이트에서 반복작업하는 상품수정을 연속적으로 실행할 수 있는 코딩이 필요합니다.

우선 아래와 같은 과정으로 

1. 상품명수정
2. 상세페이지 수정
5. 업로드정보 수정

모두 3개 항목의 수정을 순서대로 진행하는 로직을 만들어야 합니다.


step1. 이런 작업을 진행하기 위해서는 
가장 먼저 아이디와 패스워드를 이용해 https://www.percenty.co.kr/ 에 로그인할 수 있도록 합니다.
사용하는 아이디는 onepick2019@gmail.com 이고 패스워드는 qnwkehlwk8*

step2. 이번 수정과정에서는 '그룹상품관리' 화면에서 상품수정을 진행하지만
앞으로 추가로 개발할 때에는 '신규상품등록'과 '그룹상품관리', '마켓설정' 화면도 사용할 것이므로
미리 각각의 4개 화면에 대해 '바로가기' 코드를 정의해주면 좋습니다.

바로가기는 아래의 코드를 참고하면 됩니다.

<li role="menuitem" tabindex="-1" class="ant-menu-item ant-menu-item-selected ant-menu-item-only-child" data-menu-id="rc-menu-uuid-26990-1-PRODUCT_REGISTER" style="padding-left: 48px;"><span class="ant-menu-title-content">신규 상품 등록</span></li>

<li role="menuitem" tabindex="-1" class="ant-menu-item ant-menu-item-only-child" data-menu-id="rc-menu-uuid-26990-1-PRODUCT_MANAGE" style="padding-left: 48px;"><span class="ant-menu-title-content">등록 상품 관리</span></li>

<li role="menuitem" tabindex="-1" aria-disabled="false" class="ant-menu-item ant-menu-item-only-child" data-menu-id="rc-menu-uuid-26990-1-PRODUCT_GROUP" style="padding-left: 48px;"><span class="ant-menu-title-content">그룹 상품 관리</span></li>

<li role="menuitem" tabindex="-1" aria-disabled="false" class="ant-menu-item ant-menu-item-only-child" data-menu-id="rc-menu-uuid-26990-1-MARKET_SETTING" style="padding-left: 48px;"><span class="ant-menu-title-content">마켓 설정</span></li>


step3: 위와 같이 준비가 되었으면, 이제 '그룹상품관리' 화면에서 상품수에 따라 화면 로딩시간이 길어질 수 있으니, 50개씩 보기로 되어 있으면 20개 보기로 바꿔주는 거것이 필요해. 

아래의 코드를 참고해서, title="20개씩 보기" 를 선택하도록 코드를 만들어주세요.

<div class="ant-col css-1li46mu"><div class="ant-select ant-select-borderless css-1li46mu ant-select-single ant-select-show-arrow"><div class="ant-select-selector"><span class="ant-select-selection-search"><input type="search" autocomplete="off" class="ant-select-selection-search-input" role="combobox" aria-expanded="false" aria-haspopup="listbox" aria-owns="rc_select_569_list" aria-autocomplete="list" aria-controls="rc_select_569_list" readonly="" unselectable="on" value="" id="rc_select_569" style="opacity: 0;"></span><span class="ant-select-selection-item" title="20개씩 보기">20개씩 보기</span></div><span class="ant-select-arrow" unselectable="on" aria-hidden="true" style="user-select: none;"><span role="img" aria-label="down" class="anticon anticon-down ant-select-suffix"><svg viewBox="64 64 896 896" focusable="false" data-icon="down" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M884 256h-75c-5.1 0-9.9 2.5-12.9 6.6L512 654.2 227.9 262.6c-3-4.1-7.8-6.6-12.9-6.6h-75c-6.5 0-10.3 7.4-6.5 12.7l352.6 486.1c12.8 17.6 39 17.6 51.7 0l352.6-486.1c3.9-5.3.1-12.7-6.4-12.7z"></path></svg></span></span></div></div>

<div class="ant-col css-1li46mu"><div class="ant-select ant-select-borderless css-1li46mu ant-select-single ant-select-show-arrow"><div class="ant-select-selector"><span class="ant-select-selection-search"><input type="search" autocomplete="off" class="ant-select-selection-search-input" role="combobox" aria-expanded="false" aria-haspopup="listbox" aria-owns="rc_select_569_list" aria-autocomplete="list" aria-controls="rc_select_569_list" readonly="" unselectable="on" value="" id="rc_select_569" style="opacity: 0;"></span><span class="ant-select-selection-item" title="50개씩 보기">50개씩 보기</span></div><span class="ant-select-arrow" unselectable="on" aria-hidden="true" style="user-select: none;"><span role="img" aria-label="down" class="anticon anticon-down ant-select-suffix"><svg viewBox="64 64 896 896" focusable="false" data-icon="down" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M884 256h-75c-5.1 0-9.9 2.5-12.9 6.6L512 654.2 227.9 262.6c-3-4.1-7.8-6.6-12.9-6.6h-75c-6.5 0-10.3 7.4-6.5 12.7l352.6 486.1c12.8 17.6 39 17.6 51.7 0l352.6-486.1c3.9-5.3.1-12.7-6.4-12.7z"></path></svg></span></span></div></div>


=========================

그럼 1개의 상품수정을 하는 과정에 대해 설명합니다.

step4. 아래 과정은 1개 상품에 대한 상품수정 과정입니다. 이 과정을 잘 만들어, 더 이상 작업할 상품이 없을 때까지 반복해서 실행되도록
코딩을 해주면 됩니다.

1) 먼저, 수정하려는 상품목록을 보기위해서 '비그룹상품보기'로 전환해야 합니다.

디폴트는 그룹상품보기가 OFF 상태인데, button 을 클릭하면, 아래처럼 '비그룹상품보기'로 화면이 바뀐다. 아래의 2개 코드를 확인해서 '비그룹상품보기' 화면을 전환해주면 됩니다.

<div class="ant-col css-1li46mu" style="padding-left: 8px; padding-right: 8px; flex: 0 0 120px; min-width: 0px;"><span class="sc-cvnYLt jkvQdI Body3Regular14 CharacterTitle85">그룹상품 보기</span><div class="ant-row css-1li46mu" style="margin-top: 13px;"><button type="button" role="switch" aria-checked="true" class="ant-switch css-1li46mu ant-switch-checked"><div class="ant-switch-handle"></div><span class="ant-switch-inner"><span class="ant-switch-inner-checked"></span><span class="ant-switch-inner-unchecked"></span></span></button></div></div>

<div class="ant-col css-1li46mu" style="padding-left: 8px; padding-right: 8px; flex: 0 0 120px; min-width: 0px;"><span class="sc-cvnYLt jkvQdI Body3Regular14 CharacterTitle85">비그룹상품 보기</span><div class="ant-row css-1li46mu" style="margin-top: 13px;"><button type="button" role="switch" aria-checked="false" class="ant-switch css-1li46mu"><div class="ant-switch-handle"></div><span class="ant-switch-inner"><span class="ant-switch-inner-checked"></span><span class="ant-switch-inner-unchecked"></span></span></button></div></div>

2). 비그룹상품보기 화면에 보이는 20개의 상품은 모두 아래와 같은 코드로 구분되어져 있습니다. 첫번재에 보이는 상품을 수정하고 다른그룹으로 이동해주면 두번째에 있던 상품이 다시 첫번째 상품으로 화면이 바뀌게 됩니다.

따라서 첫번째 상품을 수정하고 다른그룹으로 이동시켜주는 코딩도 필요합니다. 

그럼 먼저 첫번째 상품은 첫번째로 보이는 <tr class="ant-table-row ant-table-row-level-0" 로 시작하는 부분에서 

상품명을 표시하는 부분을 클릭해서 상품수정을 할 수 있는 새로운 팝업화면이 열리도록 해야 합니다.

<div class="sc-fremEr sc-hpGnlu jzrnSR kmHLPs"><div class="ant-row ant-row-middle css-1li46mu" style="margin-left: -4px; margin-right: -4px; row-gap: 4px;"></div><div class="ant-flex css-1li46mu ant-flex-align-stretch ant-flex-vertical"><span class="sc-cQCQeq sc-inyXkq gRsusi ekgdbp">여성 빈티지 배색 원피스 H16Z1</span>

상품 1개를 감싸고 있는 전체코드는 아래와 같습니다. 확인해서 정확하게 상품수정을 위한 새로운 화면이 열리도록 해주세요.

<tr class="ant-table-row ant-table-row-level-0" data-row-key="681ae0eaef767b5120d3b35b"><td class="ant-table-cell ant-table-selection-column"><label class="ant-checkbox-wrapper css-1li46mu"><span class="ant-checkbox ant-wave-target css-1li46mu"><input class="ant-checkbox-input" type="checkbox"><span class="ant-checkbox-inner"></span></span></label></td><td colspan="7" class="ant-table-cell" style="padding: 0px;"><div class="ant-flex css-1li46mu ant-flex-align-stretch ant-flex-vertical"><div class="ant-flex css-1li46mu ant-flex-align-center"><div class="sc-fremEr sc-etVdmn iNRLIR fqTwhY"><span><div class="ant-ribbon-wrapper css-1li46mu"><div class="sc-bStcSt eqWEOt"><img draggable="false" src="https://file.percenty.co.kr/public/67e34c66a929bc2395905898/products/681ae0eaef767b5120d3b35b/312dfb23-5ef3-4623-b070-799848457fcc.jpg" class="sc-iaJaUu eSVKlt"></div><div class="ant-ribbon ant-ribbon-placement-start css-1li46mu" style="background: rgb(64, 169, 255); display: none; top: 0px;"><span class="ant-ribbon-text">AI</span><div class="ant-ribbon-corner" style="color: rgb(64, 169, 255);"></div></div></div></span></div><div class="sc-fremEr sc-hpGnlu jzrnSR kmHLPs"><div class="ant-row ant-row-middle css-1li46mu" style="margin-left: -4px; margin-right: -4px; row-gap: 4px;"></div><div class="ant-flex css-1li46mu ant-flex-align-stretch ant-flex-vertical"><span class="sc-cQCQeq sc-inyXkq gRsusi ekgdbp">여성 빈티지 배색 원피스 H16Z1</span><div class="sc-etlCFv jcxHzL ant-flex css-1li46mu"><div class="sc-cYYuRe biEWdr ant-flex css-1li46mu ant-flex-align-center"><span class="sc-cQCQeq sc-eFRcpv gRsusi eGFIWr">판매가</span><div class="ant-divider css-1li46mu ant-divider-vertical" role="separator"></div><span>37,600 원</span></div><div class="sc-cYYuRe biEWdr ant-flex css-1li46mu ant-flex-align-center"><span class="sc-cQCQeq sc-eFRcpv gRsusi eGFIWr">원가</span><div class="ant-divider css-1li46mu ant-divider-vertical" role="separator"></div><span>8,000 원 (¥ 40)</span></div><div class="sc-cYYuRe biEWdr ant-flex css-1li46mu ant-flex-align-center"><div class="sc-kbousE eVsrCX ant-flex css-1li46mu ant-flex-align-center"><div class="ant-flex css-1li46mu ant-flex-align-center"><span class="sc-cQCQeq sc-eFRcpv gRsusi eGFIWr">해외 배송비</span><div class="ant-divider css-1li46mu ant-divider-vertical" role="separator"></div></div><div class="sc-fifgRP jxBBjh"><span>14,000<span> 원</span></span><button type="button" class="ant-btn css-1li46mu ant-btn-default ant-btn-sm ant-btn-icon-only sc-dBmzty BYclj"><span class="ant-btn-icon"><span role="img" aria-label="edit" class="anticon anticon-edit"><svg viewBox="64 64 896 896" focusable="false" data-icon="edit" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M257.7 752c2 0 4-.2 6-.5L431.9 722c2-.4 3.9-1.3 5.3-2.8l423.9-423.9a9.96 9.96 0 000-14.1L694.9 114.9c-1.9-1.9-4.4-2.9-7.1-2.9s-5.2 1-7.1 2.9L256.8 538.8c-1.5 1.5-2.4 3.3-2.8 5.3l-29.5 168.2a33.5 33.5 0 009.4 29.8c6.6 6.4 14.9 9.9 23.8 9.9zm67.4-174.4L687.8 215l73.3 73.3-362.7 362.6-88.9 15.7 15.6-89zM880 836H144c-17.7 0-32 14.3-32 32v36c0 4.4 3.6 8 8 8h784c4.4 0 8-3.6 8-8v-36c0-17.7-14.3-32-32-32z"></path></svg></span></span></button></div></div></div></div><div><span class="Body3Regular14 CharacterSecondary45" style="cursor: pointer;"><span>681ae0eaef767b5120d3b35b</span></span></div></div></div><div class="sc-fremEr sc-gwZKzw jzwRTq hZUJXo"><div class="ant-row ant-row-no-wrap ant-row-middle css-1li46mu" style="margin-left: -16px; margin-right: -16px; row-gap: 4px;"><div class="ant-col css-1li46mu" style="padding-left: 16px; padding-right: 16px;"><button type="button" class="ant-btn css-1li46mu ant-btn-default ant-btn-icon-only" style="background: rgb(245, 245, 245); color: rgb(24, 144, 255);"><span class="ant-btn-icon"><span role="img" aria-label="line-chart" class="anticon anticon-line-chart"><svg viewBox="64 64 896 896" focusable="false" data-icon="line-chart" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M888 792H200V168c0-4.4-3.6-8-8-8h-56c-4.4 0-8 3.6-8 8v688c0 4.4 3.6 8 8 8h752c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zM305.8 637.7c3.1 3.1 8.1 3.1 11.3 0l138.3-137.6L583 628.5c3.1 3.1 8.2 3.1 11.3 0l275.4-275.3c3.1-3.1 3.1-8.2 0-11.3l-39.6-39.6a8.03 8.03 0 00-11.3 0l-230 229.9L461.4 404a8.03 8.03 0 00-11.3 0L266.3 586.7a8.03 8.03 0 000 11.3l39.5 39.7z"></path></svg></span></span></button></div></div></div><div class="sc-fremEr sc-gwZKzw ihmvTN hZUJXo"><div class="ant-select ant-select-outlined sc-ejfMa-d gSqtRB css-1li46mu ant-select-single ant-select-show-search"><div class="ant-select-selector"><span class="ant-select-selection-search"><input type="search" autocomplete="off" class="ant-select-selection-search-input" role="combobox" aria-expanded="false" aria-haspopup="listbox" aria-owns="rc_select_620_list" aria-autocomplete="list" aria-controls="rc_select_620_list" value="" id="rc_select_620"></span><span class="ant-select-selection-item"><div class="sc-fhzFiK bzAfDt ant-flex css-1li46mu ant-flex-justify-center"><span class="sc-dkmUuB fDCAuy">그룹 없음</span><span role="img" aria-label="down" class="anticon anticon-down sc-bDumWk jQNKDE"><svg viewBox="64 64 896 896" focusable="false" data-icon="down" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M884 256h-75c-5.1 0-9.9 2.5-12.9 6.6L512 654.2 227.9 262.6c-3-4.1-7.8-6.6-12.9-6.6h-75c-6.5 0-10.3 7.4-6.5 12.7l352.6 486.1c12.8 17.6 39 17.6 51.7 0l352.6-486.1c3.9-5.3.1-12.7-6.4-12.7z"></path></svg></span></div></span></div></div></div><div class="sc-fremEr sc-hqpNSm ihmvTN grSFhl"><div><span class="sc-cQCQeq gRsusi Body3Regular14 CharacterPrimary85">[정보없음]</span></div><div><span class="sc-cQCQeq gRsusi Body3Regular14 CharacterSecondary45">2025/05/07</span></div></div><div class="sc-fremEr sc-gwZKzw ihmvWp hZUJXo"><img draggable="false" src="./ic_1688_img.svg" class="sc-cDvQBt cSYYYH"></div><div class="sc-fremEr sc-gwZKzw jzwRTq hZUJXo"><button type="button" class="ant-btn css-1li46mu ant-btn-default ant-btn-icon-only" style="background: rgb(245, 245, 245); color: rgb(24, 144, 255);"><span class="ant-btn-icon"><span role="img" aria-label="file-text" class="anticon anticon-file-text"><svg viewBox="64 64 896 896" focusable="false" data-icon="file-text" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M854.6 288.6L639.4 73.4c-6-6-14.1-9.4-22.6-9.4H192c-17.7 0-32 14.3-32 32v832c0 17.7 14.3 32 32 32h640c17.7 0 32-14.3 32-32V311.3c0-8.5-3.4-16.7-9.4-22.7zM790.2 326H602V137.8L790.2 326zm1.8 562H232V136h302v216a42 42 0 0042 42h216v494zM504 618H320c-4.4 0-8 3.6-8 8v48c0 4.4 3.6 8 8 8h184c4.4 0 8-3.6 8-8v-48c0-4.4-3.6-8-8-8zM312 490v48c0 4.4 3.6 8 8 8h384c4.4 0 8-3.6 8-8v-48c0-4.4-3.6-8-8-8H320c-4.4 0-8 3.6-8 8z"></path></svg></span></span></button></div></div><div class="sc-fremEr sc-dAEZTx jzrnSR leIzGy"><div class="sc-fzQBhs DiBVP ant-flex css-1li46mu" style="gap: 8px;"><span role="img" aria-label="file-text" class="anticon anticon-file-text" style="padding: 4px; font-size: 14px;"><svg viewBox="64 64 896 896" focusable="false" data-icon="file-text" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M534 352V136H232v752h560V394H576a42 42 0 01-42-42zm-22 322c0 4.4-3.6 8-8 8H320c-4.4 0-8-3.6-8-8v-48c0-4.4 3.6-8 8-8h184c4.4 0 8 3.6 8 8v48zm200-184v48c0 4.4-3.6 8-8 8H320c-4.4 0-8-3.6-8-8v-48c0-4.4 3.6-8 8-8h384c4.4 0 8 3.6 8 8z" fill="#E6F7FF"></path><path d="M854.6 288.6L639.4 73.4c-6-6-14.1-9.4-22.6-9.4H192c-17.7 0-32 14.3-32 32v832c0 17.7 14.3 32 32 32h640c17.7 0 32-14.3 32-32V311.3c0-8.5-3.4-16.7-9.4-22.7zM602 137.8L790.2 326H602V137.8zM792 888H232V136h302v216a42 42 0 0042 42h216v494z" fill="#1890FF"></path><path d="M312 490v48c0 4.4 3.6 8 8 8h384c4.4 0 8-3.6 8-8v-48c0-4.4-3.6-8-8-8H320c-4.4 0-8 3.6-8 8zm192 128H320c-4.4 0-8 3.6-8 8v48c0 4.4 3.6 8 8 8h184c4.4 0 8-3.6 8-8v-48c0-4.4-3.6-8-8-8z" fill="#1890FF"></path></svg></span><span>G11-96|444-918117887334-H16</span></div></div></div></td></tr>

3) 상품수정을 할 수 있는 상품정보화면이 열리면, 맨처음 언급한 3개 항목을 수정하도록 합니다.

수정할 3개 항목은
1. 상품명수정
2. 상세페이지 수정
5. 업로드정보 수정
입니다.

순서대로 수정하고자 하는 내용을 설명할테니, 그대로 실행될 수 있도록 코딩해주기 바랍니다.

1. 상품명수정

상품명수정 부분의 전체코드는 아래의 내용입니다.

<div class="sc-fhzFiK iGFPsV ant-flex css-1li46mu" style="gap: 8px;"><span class="ant-input-affix-wrapper css-1li46mu ant-input-outlined" style="border: 1px solid var(--primary-6); width: calc(100% - 143px);"><input class="ant-input css-1li46mu" type="text" value="여성 빈티지 배색 원피스 H16Z1 "><span class="ant-input-suffix">23/50</span></span><button type="button" class="ant-btn css-1li46mu ant-btn-primary ant-btn-background-ghost"><span>카테고리 추천 받기</span></button></div>

먼저 지금 상품명 끝부분에 1을 추가해줍니다. 상품명을 수정하면 자동저장되므로, 
input 부분을 찾아서 현재상품명에 알파벳 A를 추가해주기만 하면 됩니다.

<input class="ant-input css-1li46mu" type="text" value="여성 빈티지 배색 원피스 H16Z1"> 
이 내용이 아래처럼 변경되어 보여지면 됩니다.
<input class="ant-input css-1li46mu" type="text" value="여성 빈티지 배색 원피스 H16Z1A">

그리고 상품명에 경고단어 또는 중복단어가 있는 경우에는 삭제하기를 해주어야 합니다.
아래의 코드에서처럼 <span>삭제하기</span> 가 보이면, 클릭해서 삭제가되는 코딩도 추가하세요.

<div class="sc-fhzFiK bPLHkf Body3Regular14  ant-flex css-1li46mu ant-flex-align-center" style="gap: 4px;"><div class="sc-eBMEME gWwpnh">경고 단어 포함: 심플</div><div class="sc-eBMEME jgkSWq"><button type="button" class="ant-btn css-1li46mu ant-btn-link ant-btn-sm" style="color: rgba(0, 0, 0, 0.45);"><span>삭제하기</span></button></div></div>

상품명수정과 경고단어 또는 중복단어 삭제하기가 마무리되면, 자동저장되고 있으므로, 별도로 저장하기를 하지 않아도 됩니다.
두번째 상세페이지를 수정하는 화면으로 이동하기 전에 로봇이 작업하는 것을 의심받지 않도록 1초에서 5초의 랜덤지연시간을 적용하세요.

2. 상세페이지 수정

상품수정화면에는 각각의 서브페이지로 이동하는 코드는 아래를 참고하면 되는데
상세페이지를 수정하려면, '상세페이지'를 클릭해서 새로운 서브페이지를 열어야 합니다.
서브페이지로 이동하는 아래내용을 참고해서 서브페이지로 가는 코드를 모두 정리해놓으면 좋겠어.

또는 이 화면에서 제공하는 단축키를 바로가기 코드로 정의해주는 것도 좋은데
순서대로 
Alt+1 은 상품명/카테고리 화면이동
Alt+2 는 옵션 화면이동
Alt+3 은 가격 화면이동
Alt+4 는 키워드 화면이동
Alt+5 는 썸네일 화면이동
Alt+6 은 상세페이지 화며이동
Alt+7 은 업로드 화면이동
이렇게 단축키를 사용하고 있으니, 
아래 코드를 참고해서 바로가기를 정의하거나, 단축키로 정의해주면 좋겠어.

<div class="ant-drawer-header" style="padding-bottom: 40px;"><div class="ant-drawer-header-title"><div class="ant-drawer-title"><div class="ant-row ant-row-middle css-1li46mu" style="margin-left: -8px; margin-right: -8px; row-gap: 0px;"><div class="ant-col css-1li46mu" style="padding-left: 8px; padding-right: 8px; flex: 1 1 auto;"><div class="sc-ixPHmS zhaFN"><div class="ant-tabs ant-tabs-top ant-tabs-card css-1li46mu"><div role="tablist" class="ant-tabs-nav"><div class="ant-tabs-nav-wrap"><div class="ant-tabs-nav-list" style="transform: translate(0px, 0px);"><div data-node-key="0" class="ant-tabs-tab ant-tabs-tab-active"><div role="tab" aria-selected="true" class="ant-tabs-tab-btn" tabindex="0" id="rc-tabs-4-tab-0" aria-controls="rc-tabs-4-panel-0"><span>상품명 / 카테고리</span></div></div><div data-node-key="1" class="ant-tabs-tab"><div role="tab" aria-selected="false" class="ant-tabs-tab-btn" tabindex="0" id="rc-tabs-4-tab-1" aria-controls="rc-tabs-4-panel-1"><span>옵션</span></div></div><div data-node-key="2" class="ant-tabs-tab"><div role="tab" aria-selected="false" class="ant-tabs-tab-btn" tabindex="0" id="rc-tabs-4-tab-2" aria-controls="rc-tabs-4-panel-2"><span>가격</span></div></div><div data-node-key="3" class="ant-tabs-tab"><div role="tab" aria-selected="false" class="ant-tabs-tab-btn" tabindex="0" id="rc-tabs-4-tab-3" aria-controls="rc-tabs-4-panel-3"><span>키워드</span></div></div><div data-node-key="4" class="ant-tabs-tab"><div role="tab" aria-selected="false" class="ant-tabs-tab-btn" tabindex="0" id="rc-tabs-4-tab-4" aria-controls="rc-tabs-4-panel-4"><span>썸네일</span></div></div><div data-node-key="5" class="ant-tabs-tab"><div role="tab" aria-selected="false" class="ant-tabs-tab-btn" tabindex="0" id="rc-tabs-4-tab-5" aria-controls="rc-tabs-4-panel-5"><span>상세페이지</span></div></div><div data-node-key="6" class="ant-tabs-tab"><div role="tab" aria-selected="false" class="ant-tabs-tab-btn" tabindex="0" id="rc-tabs-4-tab-6" aria-controls="rc-tabs-4-panel-6"><span>업로드</span></div></div><div class="ant-tabs-ink-bar ant-tabs-ink-bar-animated" style="width: 128.406px; left: 64.2031px; transform: translateX(-50%);"></div></div></div><div class="ant-tabs-nav-operations ant-tabs-nav-operations-hidden"><button type="button" class="ant-tabs-nav-more" tabindex="-1" aria-hidden="true" aria-haspopup="listbox" aria-controls="rc-tabs-4-more-popup" id="rc-tabs-4-more" aria-expanded="false" style="visibility: hidden; order: 1;"><span role="img" aria-label="ellipsis" class="anticon anticon-ellipsis"><svg viewBox="64 64 896 896" focusable="false" data-icon="ellipsis" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M176 511a56 56 0 10112 0 56 56 0 10-112 0zm280 0a56 56 0 10112 0 56 56 0 10-112 0zm280 0a56 56 0 10112 0 56 56 0 10-112 0z"></path></svg></span></button></div></div><div class="ant-tabs-content-holder"><div class="ant-tabs-content ant-tabs-content-top"><div role="tabpanel" tabindex="0" aria-hidden="false" class="ant-tabs-tabpane ant-tabs-tabpane-active" id="rc-tabs-4-panel-0" aria-labelledby="rc-tabs-4-tab-0"></div></div></div></div></div></div><div class="ant-col css-1li46mu" style="padding-left: 8px; padding-right: 8px;"></div><div class="ant-col css-1li46mu" style="padding-left: 8px; padding-right: 8px; display: flex; align-items: center; gap: 24px;"><button type="button" class="ant-btn css-1li46mu ant-btn-default sc-kqNxZD iQqJlp" disabled=""><span class="ant-btn-icon"><span role="img" aria-label="translation" class="anticon anticon-translation"><svg viewBox="64 64 896 896" focusable="false" data-icon="translation" width="1em" height="1em" fill="currentColor" aria-hidden="true"><defs><style></style></defs><path d="M140 188h584v164h76V144c0-17.7-14.3-32-32-32H96c-17.7 0-32 14.3-32 32v736c0 17.7 14.3 32 32 32h544v-76H140V188z"></path><path d="M414.3 256h-60.6c-3.4 0-6.4 2.2-7.6 5.4L219 629.4c-.3.8-.4 1.7-.4 2.6 0 4.4 3.6 8 8 8h55.1c3.4 0 6.4-2.2 7.6-5.4L322 540h196.2L422 261.4a8.42 8.42 0 00-7.7-5.4zm12.4 228h-85.5L384 360.2 426.7 484zM936 528H800v-93c0-4.4-3.6-8-8-8h-56c-4.4 0-8 3.6-8 8v93H592c-13.3 0-24 10.7-24 24v176c0 13.3 10.7 24 24 24h136v152c0 4.4 3.6 8 8 8h56c4.4 0 8-3.6 8-8V752h136c13.3 0 24-10.7 24-24V552c0-13.3-10.7-24-24-24zM728 680h-88v-80h88v80zm160 0h-88v-80h88v80z"></path></svg></span></span><span>브라우저 번역</span></button><span role="img" aria-label="close" tabindex="-1" class="anticon anticon-close" style="font-size: 18px; cursor: pointer;"><svg fill-rule="evenodd" viewBox="64 64 896 896" focusable="false" data-icon="close" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M799.86 166.31c.02 0 .04.02.08.06l57.69 57.7c.04.03.05.05.06.08a.12.12 0 010 .06c0 .03-.02.05-.06.09L569.93 512l287.7 287.7c.04.04.05.06.06.09a.12.12 0 010 .07c0 .02-.02.04-.06.08l-57.7 57.69c-.03.04-.05.05-.07.06a.12.12 0 01-.07 0c-.03 0-.05-.02-.09-.06L512 569.93l-287.7 287.7c-.04.04-.06.05-.09.06a.12.12 0 01-.07 0c-.02 0-.04-.02-.08-.06l-57.69-57.7c-.04-.03-.05-.05-.06-.07a.12.12 0 010-.07c0-.03.02-.05.06-.09L454.07 512l-287.7-287.7c-.04-.04-.05-.06-.06-.09a.12.12 0 010-.07c0-.02.02-.04.06-.08l57.7-57.69c.03-.04.05-.05.07-.06a.12.12 0 01.07 0c.03 0 .05.02.09.06L512 454.07l287.7-287.7c.04-.04.06-.05.09-.06a.12.12 0 01.07 0z"></path></svg></span></div><div class="sc-hciKdo YXgbk ant-flex css-1li46mu ant-flex-align-center ant-flex-justify-space-between"><span role="img" aria-label="file-text" class="anticon anticon-file-text" style="font-size: 16px;"><svg viewBox="64 64 896 896" focusable="false" data-icon="file-text" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M854.6 288.7c6 6 9.4 14.1 9.4 22.6V928c0 17.7-14.3 32-32 32H192c-17.7 0-32-14.3-32-32V96c0-17.7 14.3-32 32-32h424.7c8.5 0 16.7 3.4 22.7 9.4l215.2 215.3zM790.2 326L602 137.8V326h188.2zM320 482a8 8 0 00-8 8v48a8 8 0 008 8h384a8 8 0 008-8v-48a8 8 0 00-8-8H320zm0 136a8 8 0 00-8 8v48a8 8 0 008 8h184a8 8 0 008-8v-48a8 8 0 00-8-8H320z"></path></svg></span><span class="memoContent">G11-96|444-918117887334-H16</span><span role="img" aria-label="close" tabindex="-1" class="anticon anticon-close" style="color: rgba(0, 0, 0, 0.45); cursor: pointer;"><svg fill-rule="evenodd" viewBox="64 64 896 896" focusable="false" data-icon="close" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M799.86 166.31c.02 0 .04.02.08.06l57.69 57.7c.04.03.05.05.06.08a.12.12 0 010 .06c0 .03-.02.05-.06.09L569.93 512l287.7 287.7c.04.04.05.06.06.09a.12.12 0 010 .07c0 .02-.02.04-.06.08l-57.7 57.69c-.03.04-.05.05-.07.06a.12.12 0 01-.07 0c-.03 0-.05-.02-.09-.06L512 569.93l-287.7 287.7c-.04.04-.06.05-.09.06a.12.12 0 01-.07 0c-.02 0-.04-.02-.08-.06l-57.69-57.7c-.04-.03-.05-.05-.06-.07a.12.12 0 010-.07c0-.03.02-.05.06-.09L454.07 512l-287.7-287.7c-.04-.04-.05-.06-.06-.09a.12.12 0 010-.07c0-.02.02-.04.06-.08l57.7-57.69c.03-.04.05-.05.07-.06a.12.12 0 01.07 0c.03 0 .05.02.09.06L512 454.07l287.7-287.7c.04-.04.06-.05.09-.06a.12.12 0 01.07 0z"></path></svg></span></div></div></div></div></div>


상세페이지 화면에서는 아래와 같은 수정작업이 진행해도록 코딩해줘.

먼저, 메뉴의 내용을 수정해야 하는데, 관련 코드는 아래의 내용이야.
모두 4개의 버튼이 있는데 마지막에 있는 네번째 버튼을 누르면 상품메모 팝업창이 열리게 되어 있어.
정확히 상품메모 팝업창이 열리도록 잘 찾아서 코딩해줘.

<div class="ant-float-btn-group css-1li46mu ant-float-btn-group-circle ant-float-btn-group-circle-shadow" style="right: 24px; bottom: 100px;">

<button class="css-1li46mu ant-float-btn ant-float-btn-default ant-float-btn-circle" type="button"><div class="ant-float-btn-body"><div class="ant-float-btn-content"><div class="ant-float-btn-icon"><span role="img" aria-label="up" class="anticon anticon-up"><svg viewBox="64 64 896 896" focusable="false" data-icon="up" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M890.5 755.3L537.9 269.2c-12.8-17.6-39-17.6-51.7 0L133.5 755.3A8 8 0 00140 768h75c5.1 0 9.9-2.5 12.9-6.6L512 369.8l284.1 391.6c3 4.1 7.8 6.6 12.9 6.6h75c6.5 0 10.3-7.4 6.5-12.7z"></path></svg></span></div></div></div></button>

<button class="css-1li46mu ant-float-btn ant-float-btn-default ant-float-btn-circle" type="button"><div class="ant-float-btn-body"><div class="ant-float-btn-content"><div class="ant-float-btn-icon"><span role="img" aria-label="form" class="anticon anticon-form"><svg viewBox="64 64 896 896" focusable="false" data-icon="form" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M904 512h-56c-4.4 0-8 3.6-8 8v320H184V184h320c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8H144c-17.7 0-32 14.3-32 32v736c0 17.7 14.3 32 32 32h736c17.7 0 32-14.3 32-32V520c0-4.4-3.6-8-8-8z"></path><path d="M355.9 534.9L354 653.8c-.1 8.9 7.1 16.2 16 16.2h.4l118-2.9c2-.1 4-.9 5.4-2.3l415.9-415c3.1-3.1 3.1-8.2 0-11.3L785.4 114.3c-1.6-1.6-3.6-2.3-5.7-2.3s-4.1.8-5.7 2.3l-415.8 415a8.3 8.3 0 00-2.3 5.6zm63.5 23.6L779.7 199l45.2 45.1-360.5 359.7-45.7 1.1.7-46.4z"></path></svg></span></div></div></div></button>

<button class="css-1li46mu ant-float-btn ant-float-btn-default ant-float-btn-circle" type="button"><div class="ant-float-btn-body"><div class="ant-float-btn-content">
<div class="ant-float-btn-icon"><span role="img" aria-label="eye" class="anticon anticon-eye"><svg viewBox="64 64 896 896" focusable="false" data-icon="eye" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M942.2 486.2C847.4 286.5 704.1 186 512 186c-192.2 0-335.4 100.5-430.2 300.3a60.3 60.3 0 000 51.5C176.6 737.5 319.9 838 512 838c192.2 0 335.4-100.5 430.2-300.3 7.7-16.2 7.7-35 0-51.5zM512 766c-161.3 0-279.4-81.8-362.7-254C232.6 339.8 350.7 258 512 258c161.3 0 279.4 81.8 362.7 254C791.5 684.2 673.4 766 512 766zm-4-430c-97.2 0-176 78.8-176 176s78.8 176 176 176 176-78.8 176-176-78.8-176-176-176zm0 288c-61.9 0-112-50.1-112-112s50.1-112 112-112 112 50.1 112 112-50.1 112-112 112z"></path></svg></span></div></div></div></button>

<button class="css-1li46mu ant-float-btn ant-float-btn-default ant-float-btn-circle" type="button"><span class="ant-badge ant-badge-status css-1li46mu">
<div class="ant-float-btn-body"><div class="ant-float-btn-content">
<div class="ant-float-btn-icon"><span role="img" aria-label="file-text" class="anticon anticon-file-text"><svg viewBox="64 64 896 896" focusable="false" data-icon="file-text" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M854.6 288.6L639.4 73.4c-6-6-14.1-9.4-22.6-9.4H192c-17.7 0-32 14.3-32 32v832c0 17.7 14.3 32 32 32h640c17.7 0 32-14.3 32-32V311.3c0-8.5-3.4-16.7-9.4-22.7zM790.2 326H602V137.8L790.2 326zm1.8 562H232V136h302v216a42 42 0 0042 42h216v494zM504 618H320c-4.4 0-8 3.6-8 8v48c0 4.4 3.6 8 8 8h184c4.4 0 8-3.6 8-8v-48c0-4.4-3.6-8-8-8zM312 490v48c0 4.4 3.6 8 8 8h384c4.4 0 8-3.6 8-8v-48c0-4.4-3.6-8-8-8H320c-4.4 0-8 3.6-8 8z"></path></svg></span></div></div></div><sup data-show="true" class="ant-scroll-number ant-badge-dot" style="background: rgb(24, 144, 255);"></sup></span></button></div>


상품메모 팝업창이 열리면, 메모 내용을 전체복사하고, 현재의 메모 내용 뒷부분에 '-S' 를 추가해줘.
예를 들어, 상품메모 팝업창에 
G11-96|444-918117887334-H16
이런 내용이 있으면, 먼저 전체를 복사하고
G11-96|444-918117887334-H16-S 처럼 뒷부분에 -S 를 추가해줘.
이건 상품수정작업을 한 것과 하지 않은 것을 구분하기 위한 방법이야.

그리고, 상품메모의 변경된 내용을 저장하기 전에 반드시 

아래의 체크박스 부분이 체크(checked) 된 상태를 확인하고 변경된 메모내용을 저장해야만 하니까, 이 부분 확실하게 확인하는 코딩도 잘 적용해줘.

이 부분이 ant-checkbox-wrapper ant-checkbox-wrapper-checked, 이 상태로 되어 있는지 확인해주고, 체크되지 않은 상태라면 반드시 체크하고 변경된 내용을 저장해주도록 해야 합니다.

<label class="ant-checkbox-wrapper ant-checkbox-wrapper-checked sc-jdUcAg fCWmBV css-1li46mu">


아래는 체크된 상태의 코드이고
<div class="ant-row ant-row-end css-1li46mu"><div class="ant-col css-1li46mu" style="flex: 1 1 auto;">
<label class="ant-checkbox-wrapper ant-checkbox-wrapper-checked sc-jdUcAg fCWmBV css-1li46mu">
<span class="ant-checkbox ant-wave-target css-1li46mu ant-checkbox-checked">
<input class="ant-checkbox-input" type="checkbox">
<span class="ant-checkbox-inner"></span></span><span>상품 목록에 메모 내용 노출하기 (최대 70자 노출)</span></label></div><div class="ant-col css-1li46mu"><span class="sc-gweoQa cwuvCU Body3Regular14 CharacterSecondary45">27 / 1000</span></div></div>

이래는 체크되지 않은 상태의 코드
<div class="ant-row ant-row-end css-1li46mu"><div class="ant-col css-1li46mu" style="flex: 1 1 auto;">
<label class="ant-checkbox-wrapper sc-jdUcAg fCWmBV css-1li46mu">
<span class="ant-checkbox ant-wave-target css-1li46mu"><input class="ant-checkbox-input" type="checkbox"><span class="ant-checkbox-inner"></span></span><span>상품 목록에 메모 내용 노출하기 (최대 70자 노출)</span></label></div><div class="ant-col css-1li46mu"><span class="sc-gweoQa cwuvCU Body3Regular14 CharacterSecondary45">27 / 1000</span></div></div>

체크된 상태로 변경되어 있는 것을 확인했으면
아래 버튼을 클릭해서 저장해주도록 해줘.

<button type="button" class="ant-btn css-1li46mu ant-btn-primary"><span>저장 후 닫기 ctrl+enter</span></button>

이제 그 다음엔 복사한 메모내용을 아래의 방법으로 상세페이지에 입력하도고 해줘

편집키 툴바에서 HTML 삽입으로 복사한 메모를 상세페이지에 입력할거야.

<div class="ck ck-toolbar ck-toolbar_grouping" role="toolbar" aria-label="편집기 툴바" tabindex="-1"> 로 시작하는 내용중에

'HTML 삽입'을 바로 할 수 있는 버튼은 아래 코드의 버튼을 클릭하면 됩니다.

<button class="ck ck-button ck-off" type="button" tabindex="-1" aria-labelledby="ck-editor__aria-label_e2f62dcbaf57f1582970104f38967d7b5" data-cke-tooltip-text="HTML 삽입" data-cke-tooltip-position="s"><svg class="ck ck-icon ck-reset_all-excluded ck-icon_inherit-color ck-button__icon" viewBox="0 0 20 20"><path d="M17 0a2 2 0 0 1 2 2v7a1 1 0 0 1 1 1v5a1 1 0 0 1-.883.993l-.118.006L19 17a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2l-.001-1.001-.116-.006A1 1 0 0 1 0 15v-5a1 1 0 0 1 .999-1L1 2a2 2 0 0 1 2-2h14zm.499 15.999h-15L2.5 17a.5.5 0 0 0 .5.5h14a.5.5 0 0 0 .5-.5l-.001-1.001zm-3.478-6.013-.014.014H14v.007l-1.525 1.525-1.46-1.46-.015.013V10h-1v5h1v-3.53l1.428 1.43.048.043.131-.129L14 11.421V15h1v-5h-.965l-.014-.014zM2 10H1v5h1v-2h2v2h1v-5H4v2H2v-2zm7 0H6v1h1v4h1v-4h1v-1zm8 0h-1v5h3v-1h-2v-4zm0-8.5H3a.5.5 0 0 0-.5.5l-.001 6.999h15L17.5 2a.5.5 0 0 0-.5-.5zM10 7v1H4V7h6zm3-2v1H4V5h9zm-3-2v1H4V3h6z"></path></svg><span class="ck ck-button__label" id="ck-editor__aria-label_e2f62dcbaf57f1582970104f38967d7b5">HTML 삽입</span></button>

버튼을 클릭하면 상세페이지에 아래 코드에 해당하는 입력창이 생긴 것이 확인될 거야
복사한 메모를 Ctrl+V 등의 방법으로 '붙여넣기' 하고, 반드시 아래의 코드 내용중에 첫번째 버튼을 클릭해서 '변경사항 저장'을 해주어야만 합니다.
변경사항 저장이 되도록 신경써서 코딩해줘.

<div class="raw-html-embed ck-widget ck-widget_with-selection-handle ck-widget_selected" data-html-embed-label="HTML 코드 조각" dir="ltr" contenteditable="false"><div class="ck ck-widget__selection-handle"><svg class="ck ck-icon ck-reset_all-excluded ck-icon_inherit-color" viewBox="0 0 16 16"><path d="M4 0v1H1v3H0V.5A.5.5 0 0 1 .5 0H4zm8 0h3.5a.5.5 0 0 1 .5.5V4h-1V1h-3V0zM4 16H.5a.5.5 0 0 1-.5-.5V12h1v3h3v1zm8 0v-1h3v-3h1v3.5a.5.5 0 0 1-.5.5H12z"></path><path fill-opacity=".256" d="M1 1h14v14H1z"></path><g class="ck-icon__selected-indicator"><path d="M7 0h2v1H7V0zM0 7h1v2H0V7zm15 0h1v2h-1V7zm-8 8h2v1H7v-1z"></path><path fill-opacity=".254" d="M1 1h14v14H1z"></path></g></svg></div><div class="raw-html-embed__content-wrapper" data-cke-ignore-events="true"><div class="raw-html-embed__buttons-wrapper">

<button class="ck ck-button raw-html-embed__save-button ck-off" type="button" tabindex="-1" aria-labelledby="ck-editor__aria-label_ebc6587edc02c300a99343fab72084098" data-cke-tooltip-text="변경사항 저장" data-cke-tooltip-position="w"><svg class="ck ck-icon ck-reset_all-excluded ck-icon_inherit-color ck-button__icon" viewBox="0 0 20 20"><path d="M6.972 16.615a.997.997 0 0 1-.744-.292l-4.596-4.596a1 1 0 1 1 1.414-1.414l3.926 3.926 9.937-9.937a1 1 0 0 1 1.414 1.415L7.717 16.323a.997.997 0 0 1-.745.292z"></path></svg><span class="ck ck-button__label" id="ck-editor__aria-label_ebc6587edc02c300a99343fab72084098">변경사항 저장</span></button>

<button class="ck ck-button raw-html-embed__cancel-button ck-off" type="button" tabindex="-1" aria-labelledby="ck-editor__aria-label_e0bfb61513c451ac9a21f7849e3ecebf1" data-cke-tooltip-text="취소" data-cke-tooltip-position="w"><svg class="ck ck-icon ck-reset_all-excluded ck-icon_inherit-color ck-button__icon" viewBox="0 0 20 20"><path d="m11.591 10.177 4.243 4.242a1 1 0 0 1-1.415 1.415l-4.242-4.243-4.243 4.243a1 1 0 0 1-1.414-1.415l4.243-4.242L4.52 5.934A1 1 0 0 1 5.934 4.52l4.243 4.243 4.242-4.243a1 1 0 1 1 1.415 1.414l-4.243 4.243z"></path></svg><span class="ck ck-button__label" id="ck-editor__aria-label_e0bfb61513c451ac9a21f7849e3ecebf1">취소</span></button></div><textarea placeholder="원시 HTML을 여기에 붙여넣으세요..." class="ck ck-reset ck-input ck-input-text raw-html-embed__source"></textarea></div><div class="ck ck-reset_all ck-widget__type-around"><div class="ck ck-widget__type-around__button ck-widget__type-around__button_before" title="블록 앞에 단락 삽입" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 8"><path d="M9.055.263v3.972h-6.77M1 4.216l2-2.038m-2 2 2 2.038"></path></svg></div><div class="ck ck-widget__type-around__button ck-widget__type-around__button_after" title="블록 뒤에 단락 삽입" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 8"><path d="M9.055.263v3.972h-6.77M1 4.216l2-2.038m-2 2 2 2.038"></path></svg></div><div class="ck ck-widget__type-around__fake-caret"></div></div></div>


여기까지 상세페이지를 수정했으면, 이제 
바로가기 Alt+7 를 이용해서 '업로드' 화면으로 이동해줘.

이 때에도 이동하기 전에, 로봇이 아님을 증명하기 위해 1초에서 5초 사이의 랜덤지연시간을 적용해줘.

업로드 화면에서는 위에서 복사해놓은 메모내용을 아래의 부분에 붙여넣기 할거야.
혹시 모르니 상품메모에서 저장한 것이 클립보드에 있는지 확인이 필요할 수도 있어. 

상품정보제공고시 필드에서 특정 위치에 복사해서 저장하고 있는 상품메모 값을 입력할거야.

아래의 코드로 확인되는 '상품정보제공고시' 가 보이는 부분을 클릭하면, 추가정보내용을 확인할 수 있어.

<div class="sc-gkRewV dENBXG"><span class="sc-hbKfVi ljqtNk H5Bold16 CharacterTitle85">상품정보제공고시</span></div>

'상품정보제공고시' 텍스트 부분을 클릭하면, 아래의 내용처럼 여러개의 input 창을 확인할 수 있어.
input 창을 정의하는 이름이 서로 다를 수 있으므로, 여기에서는
두번째 input 창에 복사해놓은 상품메모 값을 입력해주도록 코딩해주면 된다.

<div class="ant-col css-1li46mu" style="padding-left: 8px; padding-right: 8px;"><div class="sc-fGdiLE cxVbue"><span class="sc-iUHWHT gBckdf Body3Regular14 CharacterTitle85">품명</span><input autocomplete="off" placeholder="상세페이지 참조" class="ant-input css-1li46mu ant-input-outlined" type="text" value="" style="margin-top: 8px;"></div></div>

<div class="ant-col css-1li46mu" style="padding-left: 8px; padding-right: 8px;"><div class="sc-fGdiLE cxVbue"><span class="sc-iUHWHT gBckdf Body3Regular14 CharacterTitle85">모델명</span><input autocomplete="off" placeholder="상세페이지 참조" class="ant-input css-1li46mu ant-input-outlined" type="text" value="" style="margin-top: 8px;"></div></div>

<div class="ant-col css-1li46mu" style="padding-left: 8px; padding-right: 8px;"><div class="sc-fGdiLE cxVbue"><span class="sc-iUHWHT gBckdf Body3Regular14 CharacterTitle85">인증/허가 사항</span><input autocomplete="off" placeholder="상세페이지 참조" class="ant-input css-1li46mu ant-input-outlined" type="text" value="" style="margin-top: 8px;"></div></div>

여기까지 수정할 내용이 모두 마무리되었어.

지금까지 수정한 내용은 모두 자동저장되었지만, 그래도 확인하기 위해
화면 하단에 있는 [저장하기] 버튼을 클릭해서 저장해주고, Esc 키를 눌러서 수정을 위해 열어놓은 화면을 닫도록 해줘.

저장하기 버튼은 아래 코드에 있어.

<div class="ant-col css-1li46mu" style="padding-left: 4px; padding-right: 4px;"><button type="button" class="ant-btn css-1li46mu ant-btn-primary"><span>저장하기</span></button></div>

수정이 완료되면, 두번째 상품에 동일한 수정작업을 진행하기 전에, 방금 작업한 상품을 다른 그룹으로 이동시켜주어야 해.

아래와 같은 방법으로 '신규수집'으로 정의되어 있는 그룹으로 이동시켜줘. 그래야, 두번째에 있던 상품이 첫번째 위치로 이동하게 된다.
그러면, 위에서 작업한 내용을 그대로 반복해서 실행해주기만 하면 되니까.

첫번째 상품의 앞부분에 아래 코드로 구분되는 체크박스가 있어

<span class="ant-checkbox ant-wave-target css-1li46mu"><input class="ant-checkbox-input" type="checkbox"><span class="ant-checkbox-inner"></span></span>

먼저 첫번째 상품이 선택되도록 체크박스를 클릭해주고
그다음에는 그룹지정 화면을 열어서 이동할 그룹을 선택하고 저장해주면 되는거야.

아래의 코드를 찾아서 버튼을 클릭하면 선택한 상품을 다른 그룹으로 이동하는 팝업창이 열릴거야.

<div class="ant-flex css-1li46mu"><div class="ant-btn-group css-1li46mu"><button type="button" class="ant-btn css-1li46mu ant-btn-default"><span>그룹 지정</span></button></div></div>

그룹지정 팝업창이 열리면
아래의 내용처럼 이동할 수 있는 50개의 그룹 목록을 확인할 수 있어.

이후에 추가로 개발하려는 코딩에서, 모든 그룹의 위치를 알고 있어야 하니까
이 부분도 50개 그룹 각각에 대해서 원하는 그룹을 쉽게 선택할 수 있도록 코딩해놓으면 좋을 것 같아.

<div class="ant-radio-group ant-radio-group-outline css-1li46mu">
<label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="fd6ef52e-4a2f-45f0-bc31-a64dd2be01f6"><span class="ant-radio-inner"></span></span><span>신규수집</span></label>
<label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="ec9421bd-61f7-47c1-bc0c-122ec55552fd"><span class="ant-radio-inner"></span></span><span>번역대기</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="906c509c-78c5-47e6-ba4d-51064eaa9d6c"><span class="ant-radio-inner"></span></span><span>등록실행</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="c3ea31c3-9af1-4ce4-8c93-4ca5f32cc208"><span class="ant-radio-inner"></span></span><span>등록A</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="5d3f5e13-6bd7-4dab-97ae-b71cff4394fa"><span class="ant-radio-inner"></span></span><span>등록B</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="d95032aa-8583-43b2-9262-a5aa1fb11e2e"><span class="ant-radio-inner"></span></span><span>등록C</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="4fefe447-7acb-42e0-8843-2a96e44abbc0"><span class="ant-radio-inner"></span></span><span>등록D</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="66e2e728-4b81-4b69-bb92-6020d0d19092"><span class="ant-radio-inner"></span></span><span>쇼핑몰T</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="1985c3bd-ded2-46e3-87c4-5b30fa17a2c1"><span class="ant-radio-inner"></span></span><span>쇼핑몰A1</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="fe3dbc70-1f4c-46f6-8ee7-73389d044eee"><span class="ant-radio-inner"></span></span><span>쇼핑몰A2</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="ba7b0717-89e5-42df-a023-dcf94eda3180"><span class="ant-radio-inner"></span></span><span>쇼핑몰A3</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="d61e8a50-057d-444d-aec9-4db019c0276b"><span class="ant-radio-inner"></span></span><span>쇼핑몰B1</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="bec47065-b409-44a6-950d-fb933477311f"><span class="ant-radio-inner"></span></span><span>쇼핑몰B2</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="5a704fe5-fd29-49cf-9316-b16f55ac7b5c"><span class="ant-radio-inner"></span></span><span>쇼핑몰B3</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="643b6da8-6ec4-48e6-8088-718a64c3241a"><span class="ant-radio-inner"></span></span><span>쇼핑몰C1</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="c7088f0c-b66e-4cde-a7c0-151862e8faa1"><span class="ant-radio-inner"></span></span><span>쇼핑몰C2</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="7ab4fd1f-b635-4226-8f9c-9079bbb65b7e"><span class="ant-radio-inner"></span></span><span>쇼핑몰C3</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="8bad1994-9b78-4bd7-99f5-a111c3d62c60"><span class="ant-radio-inner"></span></span><span>쇼핑몰D1</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="6ff29bb3-2a10-4632-adf5-a6783d9bb771"><span class="ant-radio-inner"></span></span><span>쇼핑몰D2</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="062109d4-2acf-4092-956c-b8448d72253d"><span class="ant-radio-inner"></span></span><span>쇼핑몰D3</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="0cd1bcaf-df4c-453d-b25b-5059a8e3a52a"><span class="ant-radio-inner"></span></span><span>완료A1</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="76a7f09d-16e8-4362-a38b-ba0a7cb2c223"><span class="ant-radio-inner"></span></span><span>완료A2</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="efb0f5ab-c6a1-480c-a209-85792fac2e7c"><span class="ant-radio-inner"></span></span><span>완료A3</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="4156364a-901c-47b3-a44e-caaa8c581ae0"><span class="ant-radio-inner"></span></span><span>완료B1</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="9090c7cb-d012-4a3b-a48a-72f4203e37ee"><span class="ant-radio-inner"></span></span><span>완료B2</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="a33416a3-f20c-4e72-a7e0-3f82ac5fd275"><span class="ant-radio-inner"></span></span><span>완료B3</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="b4d761b3-01e2-4049-b8a2-0954aac74d7c"><span class="ant-radio-inner"></span></span><span>완료C1</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="d6207f1f-f2d3-47ca-a75c-3972a087fac1"><span class="ant-radio-inner"></span></span><span>완료C2</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="e01517b5-6dc3-4f72-88cf-101d56a8edc1"><span class="ant-radio-inner"></span></span><span>완료C3</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="313272b5-12b9-4dc9-91c1-f8cc6f26e959"><span class="ant-radio-inner"></span></span><span>완료D1</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="45f50cc6-fc79-4d92-b665-2c3d4fe259ec"><span class="ant-radio-inner"></span></span><span>완료D2</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="1b603cd9-ae9f-4223-bca1-3e619dfd773d"><span class="ant-radio-inner"></span></span><span>완료D3</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="785073fb-d1a6-442d-b9c3-aaf8cbd99156"><span class="ant-radio-inner"></span></span><span>수동번역</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="e326979b-99b2-45e6-b127-93499cb92eeb"><span class="ant-radio-inner"></span></span><span>등록대기</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="07758d34-5da1-4eaa-9c04-68742aa23c29"><span class="ant-radio-inner"></span></span><span>번역검수</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="1e9b1827-8520-41d6-85d9-0eda8b539227"><span class="ant-radio-inner"></span></span><span>서버1</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="2f79997b-9c42-47b2-856c-c19566f6db81"><span class="ant-radio-inner"></span></span><span>서버2</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="369010a2-f5ef-4cd8-8445-dc81fff20888"><span class="ant-radio-inner"></span></span><span>서버3</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="6d8598c5-1598-4d5c-bb22-490aa83f01b0"><span class="ant-radio-inner"></span></span><span>대기1</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="9d87d517-d827-4932-a246-a40810eb8a43"><span class="ant-radio-inner"></span></span><span>대기2</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="973858ff-8184-40a0-815b-a8c26d10f991"><span class="ant-radio-inner"></span></span><span>대기3</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="72fadcf1-25ac-4a10-a780-361f29675e1a"><span class="ant-radio-inner"></span></span><span>수동1</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="214bea2e-67a8-467f-81d5-3b07cf9b25ce"><span class="ant-radio-inner"></span></span><span>수동2</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="9fabdfed-2a4d-43b0-8f91-196084615005"><span class="ant-radio-inner"></span></span><span>수동3</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="f4cb4329-6acb-4966-9133-66bec6e43e9c"><span class="ant-radio-inner"></span></span><span>검수1</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="cf717f3b-09d8-4905-bdd8-081ffdb14eb9"><span class="ant-radio-inner"></span></span><span>검수2</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="8c33a3c7-7e35-4080-9823-9dd297c95803"><span class="ant-radio-inner"></span></span><span>검수3</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="a4b644ff-3888-4a2f-93cb-d735c2d3561e"><span class="ant-radio-inner"></span></span><span>복제X</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="2c3d4081-7c62-4d11-b37e-0c57dfd9738e"><span class="ant-radio-inner"></span></span><span>삭제X</span></label><label class="ant-radio-wrapper css-1li46mu"><span class="ant-radio ant-wave-target"><input class="ant-radio-input" type="radio" value="c7959e41-fa60-4bfe-adf8-582be22d82fd"><span class="ant-radio-inner"></span></span><span>중복X</span></label>;</div>

지금은 첫번째 label 인 '신규수집'을 선택하고 
아래의 [확인] 버튼을 눌러서 그룹이동이 되도록 해줘.
<button type="button" class="ant-btn css-1li46mu ant-btn-primary"><span>확인</span></button>

첫번째 lablel 을 선택하면, 이래처럼 코드내용이 변경되고 있으미, 첫번째 lable이 정확하게 선택되었는지 확인할 수 있을거야.

<label class="ant-radio-wrapper ant-radio-wrapper-checked css-1li46mu"><span class="ant-radio ant-wave-target ant-radio-checked"><input class="ant-radio-input" type="radio" value="fd6ef52e-4a2f-45f0-bc31-a64dd2be01f6"><span class="ant-radio-inner"></span></span><span>신규수집</span></label>

이렇게 해서, 
1. 그룹상품관리 화면을 연다.
2. 비그룹상품보기로 화면을 바꾼다.
3. 첫번째 상품을 선택해서 상품명, 상세페이지, 업로드 화면에서 수정작업을 한다.
4. 마지막으로 수정한 상품은 '신규수집' 그룹으로 이동시킨다.

그리고 다시 위의 과정을 반복해서
비그룹상풉보기에 상품이 검색되지 않을때까지 반복적으로 실행해서
비그룹상품보기에 있는 모든 상품이 신규그룹으로 이동되도록
코딩을 해주면 됩니다.

부탁합니다.
