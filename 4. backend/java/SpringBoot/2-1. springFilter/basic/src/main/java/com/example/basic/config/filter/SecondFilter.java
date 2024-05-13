package com.example.basic.config.filter;

import java.io.IOException;

import jakarta.servlet.Filter;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.ServletRequest;
import jakarta.servlet.ServletResponse;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class SecondFilter implements Filter {

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {
        // TODO Auto-generated method stub
        log.info("[SecondFilter][doFilter] Start");
        HttpServletRequest req = (HttpServletRequest) request;
        HttpServletResponse res = (HttpServletResponse) response;
        if(req.getMethod().equals("GET") && req.getRequestURI().equals("/api/v1/product/hello")) {
            log.info("[SecondFilter][doFilter] sendRedirect");
            res.sendRedirect("/api/v1/user/hello");
        }

        chain.doFilter(req, res);
    }
    
}
