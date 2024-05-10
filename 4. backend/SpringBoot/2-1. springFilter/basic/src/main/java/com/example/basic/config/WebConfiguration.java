package com.example.basic.config;

import java.util.List;

import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import com.example.basic.config.filter.FirstFilter;
import com.example.basic.config.filter.SecondFilter;

@Configuration
public class WebConfiguration {
    
    @Bean
    public FilterRegistrationBean<FirstFilter> firstFilterBean() {

        FilterRegistrationBean<FirstFilter> filterBean = new FilterRegistrationBean<>(new FirstFilter());
        // secondFilterBean보다 먼저 실행 
        filterBean.setOrder(1);
        // 모든 요청에서 실행 
        filterBean.setUrlPatterns(List.of("/*"));

        return filterBean;
    }

    @Bean
    public FilterRegistrationBean<SecondFilter> secondFilterBean() {

        FilterRegistrationBean<SecondFilter> filterBean = new FilterRegistrationBean<>(new SecondFilter());
        // firstFilterBean보다 늦게 실행 
        filterBean.setOrder(2);
        // /api/v1/product/ 인 경우에서만 실행 
        filterBean.setUrlPatterns(List.of("/api/v1/product/*"));

        return filterBean;
    }

}
