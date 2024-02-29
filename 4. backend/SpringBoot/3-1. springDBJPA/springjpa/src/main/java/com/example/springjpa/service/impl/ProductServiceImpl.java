package com.example.springjpa.service.impl;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.springjpa.model.dao.ProductDao;
import com.example.springjpa.model.dto.ProductDto;
import com.example.springjpa.model.entity.ProductEntity;
import com.example.springjpa.service.ProductService;

@Service
public class ProductServiceImpl implements ProductService {

    @Autowired
    private ProductDao productDao;

    @Override
    public ProductDto findByProductName(String productName) {
        // TODO Auto-generated method stub
        ProductEntity entity = productDao.findByProductName(productName);
        ProductDto dto = new ProductDto();
        dto.setProductName(productName);
        dto.setProductPrice(entity.getProductPrice());
        dto.setCompanyName(entity.getCompanyName());

        return dto;
    }

    @Override
    public void insertProduct(ProductDto dto) {
        // TODO Auto-generated method stub
        ProductEntity entity = new ProductEntity();
        entity.setProductName(dto.getProductName());
        entity.setProductPrice(dto.getProductPrice());
        entity.setCompanyName(dto.getCompanyName());

        productDao.insertProduct(entity);
    }

    @Override
    public void deleteProduct(String productName) {
        // TODO Auto-generated method stub
        ProductEntity entity = productDao.findByProductName(productName);
        productDao.deleteProduct(entity.getId());
    }

    @Override
    public void updateProduct(ProductDto dto) {
        // TODO Auto-generated method stub
        ProductEntity entity = productDao.findByProductName(dto.getProductName());

        if(dto.getProductPrice() > 0) {
            entity.setProductPrice(dto.getProductPrice());
        }
        if(dto.getCompanyName() != null) {
            entity.setCompanyName(dto.getCompanyName());
        }

        productDao.updateProduct(entity);
    }
    
}
