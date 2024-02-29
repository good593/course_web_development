package com.example.springjpa.model.entity;

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
import lombok.ToString;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@ToString
@Entity(name = "ProductEntity")
@Table(name = "product")
public class ProductEntity {
    // id
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private Long id;

    // 일반 컬럼
    @Column(unique = true)
    private String productName;
    private int productPrice;
    private String companyName;
}
