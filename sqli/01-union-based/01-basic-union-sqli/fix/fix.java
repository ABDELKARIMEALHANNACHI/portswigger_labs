@RestController
public class ProductController {

```
@Autowired
JdbcTemplate jdbc;

@GetMapping("/products")
public List<Map<String,Object>> products(
    @RequestParam String category
) {

    String sql =
        "SELECT id,name,price FROM products WHERE category=?";

    return jdbc.queryForList(sql, category);
}
```

}
