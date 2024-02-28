package com.example.springbasic.config;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Lazy;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import com.example.springbasic.config.interceptor.BasicInterceptor;

@Configuration
public class WebMvcConfig implements WebMvcConfigurer {

    // @Override
    // public void addInterceptors(InterceptorRegistry registry) {
    //     // TODO Auto-generated method stub
    //     registry.addInterceptor(new BasicInterceptor())
    //         .addPathPatterns("/api/v1/get/*") // 적용할 url pattern
    //         .excludePathPatterns("/api/v1/post/*"); // 제외할 url pattern

    //     WebMvcConfigurer.super.addInterceptors(registry);
    // }

    @Lazy
    @Autowired
    private BasicInterceptor basicInterceptor;

    @SuppressWarnings("null")
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        // TODO Auto-generated method stub
        registry.addInterceptor(basicInterceptor)
            .addPathPatterns("/**") // 적용할 url pattern
            .excludePathPatterns("/api/v1/post/*"); // 제외할 url pattern

        WebMvcConfigurer.super.addInterceptors(registry);
    }
    
}
