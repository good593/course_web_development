package com.example.exceptionbasic.model.dto;

import com.example.exceptionbasic.constant.ProductTypeConstant;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.PositiveOrZero;
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
@Entity
@Table(name = "product")
public class ProductDto {
    @Id
    @NotBlank
    private String productId;
    @PositiveOrZero
    @Min(value = 100)
    private int productPrice;
    @NotBlank
    private String productType;

    public ProductTypeConstant checkProductType() {
        
        return ProductTypeConstant.valueOf(this.productType);
    }
}
