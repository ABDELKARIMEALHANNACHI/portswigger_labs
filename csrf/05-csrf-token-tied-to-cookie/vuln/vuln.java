@RestController
public class AccountController {

    @PostMapping("/my-account/change-email")
    public RedirectView changeEmail(
        @RequestParam String email,
        HttpSession session
    ) {

        userService.updateEmail(
            (String) session.getAttribute("username"),
            email
        );

        return new RedirectView("/my-account");
    }
}
