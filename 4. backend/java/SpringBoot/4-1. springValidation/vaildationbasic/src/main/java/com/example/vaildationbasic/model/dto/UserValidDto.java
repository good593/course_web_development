package com.example.vaildationbasic.model.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
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
public class UserValidDto {
    @NotBlank // null, "", " " > 불가능 
    private String id;
    @NotNull // null > 불가능 
    private String name;
    @NotEmpty // null, "" > 불가능 
    private String password;
    
    @PositiveOrZero
    @Max(value = 100)
    private int age;
    @Email
    private String email;
    @Pattern(regexp="^01(?:0|1|[6-9])-?\\d{3,4}-?\\d{4}$", message = "올바른 전화번로를 입력해주세요.")
    private String phoneNumber;
}
