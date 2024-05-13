package com.example.springjpa.model.dao.impl;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.springjpa.model.dao.ProductDao;
import com.example.springjpa.model.entity.ProductEntity;
import com.example.springjpa.model.repository.ProductRepository;

@Service
public class ProductDaoImpl implements ProductDao {

    @Autowired
    private ProductRepository productRepository;

    @Override
    public void deleteProduct(Long id) {
        // TODO Auto-generated method stub
        productRepository.deleteById(id);
    }

    @Override
    public ProductEntity findByProductName(String productName) {
        // TODO Auto-generated method stub
        return productRepository.findByProductName(productName);
    }

    @Override
    public void insertProduct(ProductEntity entity) {
        // TODO Auto-generated method stub
        productRepository.save(entity);
    }

    @Override
    public void updateProduct(ProductEntity entity) {
        // TODO Auto-generated method stub
        productRepository.save(entity);
    }
    
}
