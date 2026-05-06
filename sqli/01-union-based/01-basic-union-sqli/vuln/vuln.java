@RestController
public class ProductController {

```
@Autowired
JdbcTemplate jdbc;

@GetMapping("/products")
public String products(@RequestParam String category) {

    String sql =
        "SELECT id,name,price FROM products WHERE category='" +
        category + "'";

    System.out.println("[DEBUG SQL] " + sql);

    List<Map<String,Object>> rows = jdbc.queryForList(sql);

    StringBuilder html = new StringBuilder();

    for (Map<String,Object> row : rows) {

        html.append("<div>");
        html.append("<b>").append(row.get("name")).append("</b><br>");
        html.append("Price: $").append(row.get("price"));
        html.append("</div><hr>");
    }

    return html.toString();
}
```

}
