package com.example.basic.model.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
// jpa야 테이블 만들어줘~
@Table(name = "product") 
// jpa야 product테이블과 연결된 자바 클래스 이름이야!!
@Entity(name = "ProductEntity") 
public class ProductEntity {
    
    @Id // 기본키 선언!!
    @GeneratedValue(strategy = GenerationType.AUTO)
    private Long id;

    @Column(unique = true)
    private String productName;
    private int productPrice;
    private String companyName;
}
