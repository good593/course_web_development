package com.example.springbasic.config.filter;

import java.io.IOException;
import java.nio.charset.StandardCharsets;

import org.springframework.stereotype.Component;
import org.springframework.web.util.ContentCachingRequestWrapper;
import org.springframework.web.util.ContentCachingResponseWrapper;

import jakarta.servlet.Filter;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.ServletRequest;
import jakarta.servlet.ServletResponse;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Component
public class BasicFilter implements Filter {

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {
        // TODO Auto-generated method stub
        log.info("[BasicFilter][doFilter] Start");
        
        // 전처리 
        ContentCachingRequestWrapper httpRequest = new ContentCachingRequestWrapper((HttpServletRequest) request);
        ContentCachingResponseWrapper httpResponse = new ContentCachingResponseWrapper((HttpServletResponse) response);

        // 로직이 완료되면, 다음 filter 실행
        chain.doFilter(httpRequest, httpResponse);

        // 후처리 
        String uri = httpRequest.getRequestURI();
        String requestContent = new String(httpRequest.getContentAsByteArray(), StandardCharsets.UTF_8);
        String responseContent = new String(httpResponse.getContentAsByteArray(), StandardCharsets.UTF_8);

        log.info("uri: "+uri);
        log.info("requestContent: "+requestContent);
        log.info("responseContent: "+responseContent);
    }
    
}
