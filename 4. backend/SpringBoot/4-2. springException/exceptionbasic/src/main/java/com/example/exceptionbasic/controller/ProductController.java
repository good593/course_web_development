package com.example.exceptionbasic.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.exceptionbasic.model.dto.ProductDto;
import com.example.exceptionbasic.service.ProductService;

import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/v1/product")
public class ProductController {
    @Autowired
    private ProductService productService;

    // localhost:8080/api/v1/product/insert
    @PostMapping("/insert")
    public String insertProduct(@Valid @RequestBody ProductDto dto) throws Exception  {
        productService.insertProduct(dto);
        return "저장성공";
    }

    // localhost:8080/api/v1/product/select/
    @GetMapping("/select/{productName}")
    public String selectByProductName(@PathVariable String productName) throws Exception  {
        return productService.selectByProductName(productName).toString();
    }
}
