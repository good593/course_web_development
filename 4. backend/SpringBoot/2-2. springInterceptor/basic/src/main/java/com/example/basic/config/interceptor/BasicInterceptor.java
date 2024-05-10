package com.example.basic.config.interceptor;

import org.springframework.web.servlet.HandlerInterceptor;
import org.springframework.web.servlet.ModelAndView;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class BasicInterceptor implements HandlerInterceptor {

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex)
            throws Exception {

        // TODO Auto-generated method stub
        log.info("[BasicInterceptor][afterCompletion] Start");

        Long startTime = (Long)request.getAttribute("startTime");
        Long midTime = (Long)request.getAttribute("midTime");
        long endTime = System.currentTimeMillis();

        if(midTime != null) {
            log.info("Handler 동작 시간 : {} (ms)", endTime - midTime);
        }
        log.info("전체 동작 시간 : {} (ms)", endTime - startTime);

        HandlerInterceptor.super.afterCompletion(request, response, handler, ex);
    }

    @Override
    public void postHandle(HttpServletRequest request, HttpServletResponse response, Object handler,
            ModelAndView modelAndView) throws Exception {

        // TODO Auto-generated method stub
        log.info("[BasicInterceptor][postHandle] Start");

        long midTime = System.currentTimeMillis();
        request.setAttribute("midTime", midTime);

        HandlerInterceptor.super.postHandle(request, response, handler, modelAndView);
    }

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler)
            throws Exception {

        // TODO Auto-generated method stub
        log.info("[BasicInterceptor][preHandle] Start");

        long startTime = System.currentTimeMillis();
        request.setAttribute("startTime", startTime);
        
        return HandlerInterceptor.super.preHandle(request, response, handler);
    }
    
}
