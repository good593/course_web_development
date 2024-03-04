package com.example.exceptionbasic.model.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import com.example.exceptionbasic.model.dto.ProductDto;

public interface ProductRepository extends JpaRepository<ProductDto, String> {
    
}
