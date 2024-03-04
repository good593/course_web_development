package com.example.exceptionbasic.model.dto;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Max;
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
@Table(name = "user")
public class UserDto {
    @Id
    @NotBlank
    private String userId;
    @NotBlank
    private String userPw;
    @PositiveOrZero
    @Max(value = 100)
    private int userAge;
    @Email
    private String email;
    @NotBlank
    private String userType; // 일반사용자, 관리자, 매니저 
}
