package com.example.exceptionbasic.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.exceptionbasic.model.dto.ProductDto;
import com.example.exceptionbasic.model.repository.ProductRepository;

@Service
public class ProductService {
    
    @Autowired
    private ProductRepository productRepository;

    public void insertProduct(ProductDto dto) throws Exception {
        dto.checkProductType();
        productRepository.save(dto);
    }

    public ProductDto selectByProductName(String productName) throws Exception {
        return productRepository.getReferenceById(productName);
    }
}
