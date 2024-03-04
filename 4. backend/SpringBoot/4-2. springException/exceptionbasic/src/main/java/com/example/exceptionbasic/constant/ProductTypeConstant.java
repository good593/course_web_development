package com.example.exceptionbasic.constant;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public enum ProductTypeConstant {
    
    TV("tv", "텔레비전입니다.")
    , PC("pc", "컴퓨터입니다.")
    , PHONE("phone", "전화기입니다.");

    private final String productType;
    private final String productMsg;
}
