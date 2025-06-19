readme.md 에 저장된 내용에서 향후 구현 예정 기능이 아래처럼 저장되어 있다.

## 향후 구현 예정 기능

다음 기능들은 향후 구현될 예정입니다:

- 상품 목록 가져오기
- 상품 선택
- 상품명 수정 (끝에 -S 추가)
- 상세페이지 수정
- 업로드 정보 수정

좀더 구체적으로 구현할 것들을 주요 모듈별로 작성할 것이고, 내용은 아래와 같다.



상품수정의 과정은 모두 8개의 모듈을 각각 만들어 진행되도록 구성한다.
파일의 크기도 줄일 수 있고, 수정하는데 도움이 될 수 있다.

1. 비그룹상품보기에 있는 총상품수량 조사
2. 첫번째상품 수정화면 모달창 열기
3. 경고단어 또는 중복단어 삭제하기
4. 상품명 수정
5. 메모편집 수정
6. 상세페이지 수정
7. 업로드 수정
8. 수정한 상품 그룹이동


1. 비그룹상품보기에 있는 총상품수량 조사

비그룹상풉보기 화면에서는 아래의 html 코드에서 총상품수를 확인할 수 있다.
총상품수가 0개라면 이후의 작업은 모두 중단하도록 하고
총상품수가 1개 이상이라면 0개가 될 때까지 추가로 구현할 상품수정과 관련된 모듈들을 순서대로 처리하도록 한다.

<div class="sc-gRfXlQ fUISiZ Body3Regular14 CharacterPrimary85 ant-flex css-1li46mu ant-flex-align-center ant-flex-justify-left" style="gap: 12px;"><span style="padding-left: 16px;">총 249개 상품</span><div class="ant-flex css-1li46mu"><div class="ant-btn-group css-1li46mu"><button type="button" class="ant-btn css-1li46mu ant-btn-default" disabled=""><span>그룹 지정</span></button></div></div></div>

2. 첫번째상품 수정화면 모달창 열기

첫번째 상품을 클릭하면 수정화면 모달창이 열리도록 되어 있다. 
로그인후 적용했던 모달창 닫기는 수정화면 모달창에서는 적용되지 않도록 주의해야 한다. 모달창이 닫히면 수정작업을 진행할 수 없다.

비그룹상품보기 화면의 전체상품 목록은 percenty_project_goods_table_code.md 파일을 열어서 <table>.... </table> 구조를 확인해서
첫번째 상품을 어떻게 클릭해서 수정화면 모달창이 열리도록 할 것인지에 대해 스크립트를 작성한다.

첫번째 상품의 수정화면 모달창을 열기 위해서는

첫번째 상품명 부분을 클릭하는 스크립트를 만들어야 하는데
상품명을 감싸고 있는 html 코드가 아래와 같으므로
<div class="ant-flex css-1li46mu ant-flex-align-stretch ant-flex-vertical"><span class="sc-cQCQeq sc-inyXkq gRsusi ekgdbp">여성 원피스 오프숄더 드레스 여름옷 G03Z2</span>

가장 먼저 나오는 <div class="ant-flex css-1li46mu ant-flex-align-stretch ant-flex-vertical"><span class="sc-cQCQeq sc-inyXkq gRsusi ekgdbp"> 부분을 확인해서 클릭하도록 스크립트를 만들면 된다.

[수정화면 모달창에서 탭 이동이 가능한 추가 스크립트 작성]

수정화면 모달창에는 모두 7개의 탭 화면 이동이 가능한데, 수정작업을 진행하면서 항상 사용할 것이므로
미리 탭화면 이동을 위해 바로가기 단축키와 같은 스크립트를 만들어놓으면 좋을 것 같아.

percenty_project_move_tab.mb 파일에 있는 html 코드를 분석해서

상품명/카테고리 화면 바로가기
옵션 화면 바로가기
가격 화면 바로가기
키워드 화면 바로가기
썸네일 화면 바로가기
상세페이지 화면 바로가기
업로드 화면 바로가기

모두 7개의 화면에 바로가기할 수 있는 스크립트를 만들어줘.
스크립트를 만들어 놓으면, 앞으로 진행할 개발에서 탭화면을 변경할 경우, 스크립트에서 정의한 바로가기를 이용할 수 있을 것 같아.
그러면 탭화면 이동이 명확해질 것 같아. 확인하고 작성해줘

3. 경고단어 또는 중복단어 삭제하기

수정화면 모달창이 열리면, 가장 먼저 경고단어 또는 중복단어를 삭제하는 스크립트가 필요해.
아래의 코드에서처럼 <span>삭제하기</span> 가 보이면, 클릭해서 삭제가되는 스크립트를 작성하세요.

<div class="sc-fhzFiK bPLHkf Body3Regular14  ant-flex css-1li46mu ant-flex-align-center" style="gap: 4px;"><div class="sc-eBMEME gWwpnh">경고 단어 포함: 심플</div><div class="sc-eBMEME jgkSWq"><button type="button" class="ant-btn css-1li46mu ant-btn-link ant-btn-sm" style="color: rgba(0, 0, 0, 0.45);"><span>삭제하기</span></button></div></div>

4. 상품명 수정

<div class="sc-eBMEME jgkSWq"><div class="sc-eBMEME bwCVJu">국내 마켓 노출 상품명</div><div class="sc-fhzFiK iGFPsV ant-flex css-1li46mu" style="gap: 8px;"><span class="ant-input-affix-wrapper css-1li46mu ant-input-outlined" style="border: 1px solid var(--primary-6); width: calc(100% - 143px);"><input class="ant-input css-1li46mu" type="text" value="여성 원피스 오프숄더 드레스 여름옷 G03Z2"><span class="ant-input-suffix">25/50</span></span><button type="button" class="ant-btn css-1li46mu ant-btn-primary ant-btn-background-ghost"><span>카테고리 추천 받기</span></button></div><div class="sc-eBMEME iMna-dW"><div class="sc-eBMEME jgkSWq Body3Regular14 CharacterSecondary45">2506912-时尚设计感拼接撞色连衣裙露肩气质收腰礼服裙南油女夏款</div><div class="sc-eBMEME jgkSWq Body3Regular14 CharacterSecondary45">2506912- 유명한 디자인 감각 스 플라이 싱 대비 컬러 드레스 오프 숄더 기질 허리 껴안는 드레스 남부 석유 여성의 여름 스타일</div></div><div class="sc-fhzFiK bPLHkf Body3Regular14  ant-flex css-1li46mu ant-flex-align-center" style="gap: 4px;"><div class="sc-eBMEME gWwpnh"></div></div></div>


수정해야할 상품명이 있는 정확한 위치는
<input class="ant-input css-1li46mu" type="text" value="여성 원피스 오프숄더 드레스 여름옷 G03Z2">
인데, 

상품명을 수정하려면, 이 코드에서 value 부분을 복사해서 클립보드로 가져오고
클립보드에서 가져온 상품명 맨뒤에 A 문자를 추가해준다.

그리고, 기존의 value 값은 모두 지우고, 클립보드에서 새로 수정한 value 값으로 대체해서 입력해준다.


[그리고 상품명을 수정해주는 스크립트를 추가해줘.]

그리고, 첫번째 상품을 수정할 때에는, 기존의 상품명에 A를 붙여서 수정하고
두번째 상품을 수정할 때에는, 기존의 상품명에 B를 붙여서 수정하는 것처럼
영어 26개의 알파벳을 순차적으로 기존상품명에 붙여서 수정하려고 하니까
이부분이 적용되는 별도의 스크립트 작성이 필요해.
Z까지 모두 사용했으면, 27번쨰 상품에서는 다시 A부터 사용하면 된다.


5. 메모편집 수정

우선 수정화면 모달창에서 아래 코드를 참고해서, 새로운 메모편집 모달창이 정확히 열릴 수 있도록 해줘.

<button class="css-1li46mu ant-float-btn ant-float-btn-default ant-float-btn-circle" type="button"><span class="ant-badge ant-badge-status css-1li46mu"> 을 확인하면, 메모편집 모달창이 열리게 될거야. 확인해줘.

<div class="ant-float-btn-group css-1li46mu ant-float-btn-group-circle ant-float-btn-group-circle-shadow" style="right: 24px; bottom: 100px;"><button class="css-1li46mu ant-float-btn ant-float-btn-default ant-float-btn-circle" type="button"><div class="ant-float-btn-body"><div class="ant-float-btn-content"><div class="ant-float-btn-icon"><span role="img" aria-label="up" class="anticon anticon-up"><svg viewBox="64 64 896 896" focusable="false" data-icon="up" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M890.5 755.3L537.9 269.2c-12.8-17.6-39-17.6-51.7 0L133.5 755.3A8 8 0 00140 768h75c5.1 0 9.9-2.5 12.9-6.6L512 369.8l284.1 391.6c3 4.1 7.8 6.6 12.9 6.6h75c6.5 0 10.3-7.4 6.5-12.7z"></path></svg></span></div></div></div></button>

<button class="css-1li46mu ant-float-btn ant-float-btn-default ant-float-btn-circle" type="button"><span class="ant-badge ant-badge-status css-1li46mu"><div class="ant-float-btn-body"><div class="ant-float-btn-content"><div class="ant-float-btn-icon"><span role="img" aria-label="file-text" class="anticon anticon-file-text"><svg viewBox="64 64 896 896" focusable="false" data-icon="file-text" width="1em" height="1em" fill="currentColor" aria-hidden="true"><path d="M854.6 288.6L639.4 73.4c-6-6-14.1-9.4-22.6-9.4H192c-17.7 0-32 14.3-32 32v832c0 17.7 14.3 32 32 32h640c17.7 0 32-14.3 32-32V311.3c0-8.5-3.4-16.7-9.4-22.7zM790.2 326H602V137.8L790.2 326zm1.8 562H232V136h302v216a42 42 0 0042 42h216v494zM504 618H320c-4.4 0-8 3.6-8 8v48c0 4.4 3.6 8 8 8h184c4.4 0 8-3.6 8-8v-48c0-4.4-3.6-8-8-8zM312 490v48c0 4.4 3.6 8 8 8h384c4.4 0 8-3.6 8-8v-48c0-4.4-3.6-8-8-8H320c-4.4 0-8 3.6-8 8z"></path></svg></span></div></div></div><sup data-show="true" class="ant-scroll-number ant-badge-dot" style="background: rgb(24, 144, 255);"></sup></span></button></div>

메모편집 모달창이 열리면, 우선 강제로 닫히지 않도록 주의해주면 좋겠어.
메모편집에 기록되어 있는 편집내용은 아래의 코드에서 확인할 수 있다.

<textarea rows="17" placeholder="상품에 대한 메모를 작성해주세요" class="ant-input css-1li46mu ant-input-outlined">G21-96|445-916679737498-G03</textarea>

편집화면에 있는 G21-96|445-916679737498-G03 와 같은 메모내용을 모두 복사해서, 다른 모달창에 붙여넣기할 수 있도록 클립보드 등을 이용해 조치해줘.

그리고, 메모편집 모달창을 닫기 전에, 편집화면에 있는 메모내용을 아래과 같은 방법으로 수정해서 저장해줘.

기존의 메모편집내용 맨 뒷부분에 -S 를 추가해서 수정해주면 되는데, G21-96|445-916679737498-G03-S 처럼 수정해주면 된다.
그리고 기존의 편집내용은 삭제하고 수정한 편집내용으로 저장되도록 해줘.

메모편집 모달창에서 편집내용을 수정한 후, 변경된 내용을 저장하기 전에 
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


5. 상세페이지 수정

이제 메모편집 모달창에서 클립보드에 저장해놓은 G21-96|445-916679737498-G03 와 같은 메모편집내용을 상세페이지와 업로드 화면에서 필요한 부분에 붙여넣기를 진행할거야.

먼저 상세페이지에 복사한 메모편집내용을 추가해서 저장하는 것은 아래와 같은 방법으로 진행해줘.

위에서 미리 만들어 놓은 탭화면 바로가기 스크립트를 이용해 상세페이지 탭화면을 열어줘. 바로가기 스크립트를 만들지 았았다면, Alt 키를 누르고 6 을 누르면 상세페이지 탭화면이 열리니까, 참고해줘.

이제 편집키 툴바에서 'HTML 삽입' 아이콘을 클릭하고, 메모편집 모달창에서 복사한 메모내용을 상세페이지에 입력할거야.

percenty_project_editor_toolbar.md 파일에 편집기툴바와 관련된 html 코드를 정확히 확인해서
편집기툴바중 아래 코드에서 확인할 수 있는 'HTML 삽입'이 가능하도록 버튼을 클릭해줘.

<button class="ck ck-button ck-off" type="button" tabindex="-1" aria-labelledby="ck-editor__aria-label_ea10cf977bfb69e80b98e86abaa784c7e" data-cke-tooltip-text="HTML 삽입" data-cke-tooltip-position="s"><svg class="ck ck-icon ck-reset_all-excluded ck-icon_inherit-color ck-button__icon" viewBox="0 0 20 20"><path d="M17 0a2 2 0 0 1 2 2v7a1 1 0 0 1 1 1v5a1 1 0 0 1-.883.993l-.118.006L19 17a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2l-.001-1.001-.116-.006A1 1 0 0 1 0 15v-5a1 1 0 0 1 .999-1L1 2a2 2 0 0 1 2-2h14zm.499 15.999h-15L2.5 17a.5.5 0 0 0 .5.5h14a.5.5 0 0 0 .5-.5l-.001-1.001zm-3.478-6.013-.014.014H14v.007l-1.525 1.525-1.46-1.46-.015.013V10h-1v5h1v-3.53l1.428 1.43.048.043.131-.129L14 11.421V15h1v-5h-.965l-.014-.014zM2 10H1v5h1v-2h2v2h1v-5H4v2H2v-2zm7 0H6v1h1v4h1v-4h1v-1zm8 0h-1v5h3v-1h-2v-4zm0-8.5H3a.5.5 0 0 0-.5.5l-.001 6.999h15L17.5 2a.5.5 0 0 0-.5-.5zM10 7v1H4V7h6zm3-2v1H4V5h9zm-3-2v1H4V3h6z"></path></svg><span class="ck ck-button__label" id="ck-editor__aria-label_ea10cf977bfb69e80b98e86abaa784c7e">HTML 삽입</span></button>

'HTML 삽입' 버튼을 클릭하고 2초 정도 대기했다가, 메모편집 모달창에서 복사한 내용을 textarea 에 붙여넣기 하고 저장해줘.
아래의 코드를 찾아서 textarea 에 붙여넣기 해주면 된다.

<textarea placeholder="원시 HTML을 여기에 붙여넣으세요..." class="ck ck-reset ck-input ck-input-text raw-html-embed__source"></textarea>

그리고, 입력한 내용을 저장해줘.

아래의 코드에서 <button class="ck ck-button raw-html-embed__save-button ck-off" type="button" tabindex="-1" aria-labelledby="ck-editor__aria-label_e012b2997cc4c0d3af06f6455d40f5b85" data-cke-tooltip-text="변경사항 저장" data-cke-tooltip-position="w"> 의 버튼을 클릭하면 저장이 된다.

<div class="raw-html-embed__buttons-wrapper"><button class="ck ck-button raw-html-embed__save-button ck-off" type="button" tabindex="-1" aria-labelledby="ck-editor__aria-label_e012b2997cc4c0d3af06f6455d40f5b85" data-cke-tooltip-text="변경사항 저장" data-cke-tooltip-position="w"><svg class="ck ck-icon ck-reset_all-excluded ck-icon_inherit-color ck-button__icon" viewBox="0 0 20 20"><path d="M6.972 16.615a.997.997 0 0 1-.744-.292l-4.596-4.596a1 1 0 1 1 1.414-1.414l3.926 3.926 9.937-9.937a1 1 0 0 1 1.414 1.415L7.717 16.323a.997.997 0 0 1-.745.292z"></path></svg><span class="ck ck-button__label" id="ck-editor__aria-label_e012b2997cc4c0d3af06f6455d40f5b85">변경사항 저장</span></button><button class="ck ck-button raw-html-embed__cancel-button ck-off" type="button" tabindex="-1" aria-labelledby="ck-editor__aria-label_e503b9badb8d67c36e5e464e9162651d4" data-cke-tooltip-text="취소" data-cke-tooltip-position="w"><svg class="ck ck-icon ck-reset_all-excluded ck-icon_inherit-color ck-button__icon" viewBox="0 0 20 20"><path d="m11.591 10.177 4.243 4.242a1 1 0 0 1-1.415 1.415l-4.242-4.243-4.243 4.243a1 1 0 0 1-1.414-1.415l4.243-4.242L4.52 5.934A1 1 0 0 1 5.934 4.52l4.243 4.243 4.242-4.243a1 1 0 1 1 1.415 1.414l-4.243 4.243z"></path></svg><span class="ck ck-button__label" id="ck-editor__aria-label_e503b9badb8d67c36e5e464e9162651d4">취소</span></button></div>

7. 업로드 수정

이제 메모편집 모달창에서 복사한 메모내용을 업로드 탭화면에서 아래의 부분에 붙여넣기하도록 진행해줘.

아래의 코드로 확인되는 '상품정보제공고시' 가 보이는 부분을 클릭하면, 추가정보내용을 확인할 수 있어.

<div class="sc-gkRewV dENBXG"><span class="sc-hbKfVi ljqtNk H5Bold16 CharacterTitle85">상품정보제공고시</span></div>

'상품정보제공고시' 텍스트 부분을 클릭하면, 아래의 내용처럼 여러개의 input 창을 확인할 수 있어.
input 창을 정의하는 이름이 서로 다를 수 있으므로, 여기에서는
두번째 input 창에 복사해놓은 메모내용을 입력해주도록 코딩해주면 된다.

<div class="ant-col css-1li46mu" style="padding-left: 8px; padding-right: 8px;"><div class="sc-fGdiLE cxVbue"><span class="sc-iUHWHT gBckdf Body3Regular14 CharacterTitle85">품명</span><input autocomplete="off" placeholder="상세페이지 참조" class="ant-input css-1li46mu ant-input-outlined" type="text" value="" style="margin-top: 8px;"></div></div>

<div class="ant-col css-1li46mu" style="padding-left: 8px; padding-right: 8px;"><div class="sc-fGdiLE cxVbue"><span class="sc-iUHWHT gBckdf Body3Regular14 CharacterTitle85">모델명</span><input autocomplete="off" placeholder="상세페이지 참조" class="ant-input css-1li46mu ant-input-outlined" type="text" value="" style="margin-top: 8px;"></div></div>

<div class="ant-col css-1li46mu" style="padding-left: 8px; padding-right: 8px;"><div class="sc-fGdiLE cxVbue"><span class="sc-iUHWHT gBckdf Body3Regular14 CharacterTitle85">인증/허가 사항</span><input autocomplete="off" placeholder="상세페이지 참조" class="ant-input css-1li46mu ant-input-outlined" type="text" value="" style="margin-top: 8px;"></div></div>

여기까지 수정할 내용이 모두 마무리되었어.

지금까지 수정한 내용은 모두 자동저장되었지만, 그래도 확인하기 위해
화면 하단에 있는 [저장하기] 버튼을 클릭해서 저장해주고, Esc 키를 눌러서 수정을 위해 열어놓은 화면을 닫도록 해줘.

저장하기 버튼은 아래 코드에 있어.

<div class="ant-col css-1li46mu" style="padding-left: 4px; padding-right: 4px;"><button type="button" class="ant-btn css-1li46mu ant-btn-primary"><span>저장하기</span></button></div>

마지막으로 수정화면 모달창의 바깥부분을 클릭하거나, ESC 키를 눌러서 수정화면 모달창을 닫아줘.


8. 수정한 상품 그룹이동

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

==========

이제 상품수정을 하기 위해 작성한 아래의 8개 모듈이 비그룹상품보기 화면에서 총상품수량이 0이 될때까지 반복해서 실행되도록 스크립트를 구성해줘.

1. 비그룹상품보기에 있는 총상품수량 조사
2. 첫번째상품 수정화면 모달창 열기
3. 경고단어 또는 중복단어 삭제하기
4. 상품명 수정
5. 메모편집 수정
6. 상세페이지 수정
7. 업로드 수정
8. 수정한 상품 그룹이동
