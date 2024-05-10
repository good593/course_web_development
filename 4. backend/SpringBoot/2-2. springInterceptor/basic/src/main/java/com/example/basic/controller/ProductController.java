package com.example.basic.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.basic.model.ProductDto;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@RestController
@RequestMapping("/api/v1/product")
public class ProductController {
    
    // localhost:8080/api/v1/product/hello
    @GetMapping("/hello")
    public String getHello() {

        log.info("[ProductController][getHello] Start");
        return "Hello World from ProductController";
    }

    // localhost:8080/api/v1/product/get?name=name1&price=33
    @GetMapping("/get")
    public String getDto(@ModelAttribute ProductDto dto) {

        log.info("[ProductController][getDto] Start");
        return "get: "+dto.toString();
    }

    // localhost:8080/api/v1/product/post
    @PostMapping("/post")
    public String postDto(@RequestBody ProductDto dto) {

        log.info("[ProductController][postDto] Start");
        return "post: "+dto.toString();
    }

}
