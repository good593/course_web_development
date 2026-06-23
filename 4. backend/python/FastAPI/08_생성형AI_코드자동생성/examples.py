# -- 예제 요구사항 ------------------------------------------------------------

EXAMPLE_SIMPLE = """
블로그 게시글 관리 API:
- POST /posts: 게시글 작성 (title, content, author 필수)
- GET /posts: 전체 목록 조회
- GET /posts/{post_id}: 특정 게시글 조회
- PUT /posts/{post_id}: 게시글 수정
- DELETE /posts/{post_id}: 게시글 삭제

추가 요구사항:
- 존재하지 않는 게시글 404 처리
- created_at 타임스탬프 자동 부여
- PostCreate, PostUpdate, PostResponse 스키마 분리
"""

EXAMPLE_COMPLEX = """
전자상거래 주문 API:

[데이터 구조]
- Product: id, name, price(원), stock(재고 수량)
- Order: id, user_id, items(List), total_price, status, created_at
- OrderItem: product_id, quantity, unit_price

[엔드포인트]
- GET /products: 상품 목록
- POST /orders: 주문 생성
- GET /orders/{order_id}: 주문 조회
- PATCH /orders/{order_id}/cancel: 주문 취소

[비즈니스 규칙]
1. 주문 생성 시 재고 확인 (부족하면 400)
2. 재고 차감은 주문 생성 후 즉시
3. 취소는 'pending' 상태에서만 가능 (그 외 400)
4. 취소 시 재고 복구
5. total_price는 서버에서 계산 (클라이언트 입력 무시)
"""
