package com.example.basic.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import com.example.basic.config.interceptor.BasicInterceptor;

@Configuration
public class WebMvcConfig implements WebMvcConfigurer {

    @Override
    public void addInterceptors(InterceptorRegistry registry) {

        // TODO Auto-generated method stub
        registry.addInterceptor(new BasicInterceptor())
            .addPathPatterns("/**") // 적용할 url pattern
            .excludePathPatterns("/api/v1/product/**"); // 제외할 url pattern
        
        WebMvcConfigurer.super.addInterceptors(registry);
    }
    
}
