package com.example.springjpa.model.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import com.example.springjpa.model.entity.ProductEntity;

public interface ProductRepository extends JpaRepository<ProductEntity, Long> {
    
    public ProductEntity findByProductName(String productName);
}
