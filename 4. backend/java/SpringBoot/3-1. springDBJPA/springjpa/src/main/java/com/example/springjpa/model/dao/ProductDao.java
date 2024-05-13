package com.example.springjpa.model.dao;

import com.example.springjpa.model.entity.ProductEntity;

public interface ProductDao {
    // select
    public ProductEntity findByProductName(String productName);
    // insert
    public void insertProduct(ProductEntity entity);
    // update
    public void updateProduct(ProductEntity entity);
    // delete
    public void deleteProduct(Long id);
}
