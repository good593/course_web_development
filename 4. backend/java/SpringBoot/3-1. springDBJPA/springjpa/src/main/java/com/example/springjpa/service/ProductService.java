package com.example.springjpa.service;

import com.example.springjpa.model.dto.ProductDto;

public interface ProductService {
    // insert
    public void insertProduct(ProductDto dto);
    // select
    public ProductDto findByProductName(String productName);
    // update
    public void updateProduct(ProductDto dto);
    // delete
    public void deleteProduct(String productName);
}
