<div data-wuic-partial="widget" style="width: 560px">
    <div data-wuic-partial="head" style="border-bottom: 1px solid #ddd;">
      OPEN API 키 수정
      <button id="hmacIntegratorUpdateSelectPopupCloseBtn" type="button"></button>
    </div>

    <div data-wuic-partial="body">
  <form role="form" class="integratorSelectForm" id="integratorSelectForm" method="post" novalidate="novalidate">
    <div class="wing-web-component" data-wuic-props="name:form line">

      <dl><h3>업체 입력 방식</h3></dl>
      <dl style="border-top: 0">
        <dt>
          <ul class="wing-web-component" data-wuic-props="name:radio-hl">
            
            <li>
                <span class="wing-web-component" data-wuic-props="name:radio">
                  <input type="radio" class="integratorsListSelectOption" id="integratorsListSelectOption" name="integratorSelectOption" value="INTEGRATOR" checked="">
                  <label for="integratorsListSelectOption">연동업체 선택</label>
                </span>
            </li>
            
            <li>
                <span class="wing-web-component" data-wuic-props="name:radio">
                  <input type="radio" class="vendorIntegratorSelectOption" id="vendorIntegratorSelectOption" name="integratorSelectOption" value="VENDOR">
                  <label for="vendorIntegratorSelectOption">자체개발(직접입력)</label>
                </span>
            </li>
          </ul>
        </dt>
      </dl>

      <!-- 연동업체 선택 -->
      
      <dl class="integratorsListSelect" style="z-index: 999; display: flex;">
        <dt><strong>업체명</strong></dt>
        <dd>
          <div style="border: 1px solid #ccc; border-radius: 5px;">
              <span id="integratorsList" class="wing-web-component" data-wuic-props="name:txt-inp-unit unit-position:right size:l">
                <span data-wuic-partial="unit" style="border: none;"><i class="wing-web-component integratorsDropdown" data-wuic-props="name:ico icon:arrow-down"></i></span>
                <span data-wuic-partial="boxing">
                  <input id="integrator" style="border: 0px;" type="text" placeholder="업체명" class="ui-autocomplete-input" autocomplete="off">
                </span>
              </span>
          </div>
        </dd>
      </dl>
      

      <!-- 자체개발(직접입력) -->
      <dl class="vendorIntegratorSelect" style="display: none">
        <dt><strong>업체명</strong></dt>
        <dd>
            <span class="wing-web-component" data-wuic-props="name:txt-inp size:l">
              <span data-wuic-partial="boxing">
                <input id="vendorIntegratorName" name="vendorIntegratorName" class="vendorIntegratorName" type="text" placeholder="예) 자체 개발"><i></i>
              </span>
              <button data-wuic-partial="close" data-wuic-attrs="hide:true"></button>
            </span>
          <span id="vendorIntegratorName-info" class="wing-web-component vendorIntegratorName-info" data-wuic-props="name:hptxt type:success" style="color: #777777;">API를 연동할 서비스의 업체명을 입력해주세요.</span>
          <div id="vendorIntegratorName-error" class="vendorIntegratorName-error"></div>
        </dd>
      </dl>
      <dl class="vendorIntegratorSelect" style="display: none">
        <dt><strong>URL</strong></dt>
        <dd>
            <span class="wing-web-component" data-wuic-props="name:txt-inp size:l">
              <span data-wuic-partial="boxing">
                <input id="vendorIntegratorUrl" name="vendorIntegratorUrl" class="vendorIntegratorUrl" type="text" placeholder="예) www.wing.coupang.com"><i></i>
              </span>
              <button data-wuic-partial="close" data-wuic-attrs="hide:true"></button>
            </span>
            <span id="vendorIntegratorUrl-info" class="wing-web-component vendorIntegratorUrl-info" data-wuic-props="name:hptxt type:success" style="color: #777777;">API를 연동할 서비스의 URL을 입력해주세요.</span>
            <div id="vendorIntegratorUrl-error" class="vendorIntegratorUrl-error"></div>
        </dd>
      </dl>
      <dl class="vendorIntegratorSelect" style="display: none">
        <dt><strong>IP 주소</strong></dt>
        <dd>
            <span class="wing-web-component" data-wuic-props="name:txt-area size:l">
              <textarea id="vendorIntegratorIpAddresses" name="vendorIntegratorIpAddresses" class="vendorIntegratorIpAddresses" placeholder="예) 123.456.789.123"></textarea>
                <span id="vendorIntegratorIpAddresses-info" class="wing-web-component vendorIntegratorIpAddresses-info" data-wuic-props="name:hptxt type:success" style="color: #777777;">
                    API를 사용할 IP 주소가 여러 개라면 쉼표로 구분해주세요.
                </span>
            <div id="vendorIntegratorIpAddresses-error" class="vendorIntegratorIpAddresses-error"></div>
            <span id="vendorIntegratorIpAddresses-info" class="wing-web-component vendorIntegratorIpAddresses-info" data-wuic-props="name:hptxt type:success" style="color: #2B41BE">
                - 직접 개발한다면, <strong style="color: #2B41BE">내 IP 주소를 확인</strong>
                해주세요.
                (검색포털에 'IP 주소' 입력)<br>
                - 연동업체를 사용한다면, <strong style="color: #2B41BE">업체에 IP 주소를 문의</strong>
                해주세요.
            </span>
            </span>

        </dd>
      </dl>

    </div>
  </form>
</div>

    
    <div data-wuic-partial="foot" style="border-top: 1px solid #ddd;">
      <button id="hmacIntegratorUpdateSelectPopupCancelBtn" type="button" class="wing-web-component" data-wuic-props="name:btn size:m">취소</button>
      <button id="hmacIntegratorUpdateSelectPopupConfirmBtn" type="button" class="wing-web-component confirmBtn" data-wuic-props="name:btn type:primary size:m" disabled="">확인</button>
    </div>
  </div>