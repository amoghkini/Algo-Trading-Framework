# User management

Everything related to user accounts: sign-up, e-mail verification, login/logout, password change and reset, and
the profile page.

**Code:** `src/user/`, `src/restapis/{sign_up,verify_user,login,logout,password_*,my_profile}_api.py`,
`src/forms/`, `src/templates/{signup,login,profile,change_password,reset_*}.html`

## Features

### Sign-up
- Form fields: first name, last name, e-mail, password + confirmation, mobile number, date of birth.
- A **unique user name** is generated automatically from the name (`<first 5 letters of first name>_<initials>`,
  lower-case, e.g. `amogh_ak`). If it is taken, the generator walks through the other characters of the last and
  first name and finally appends a counter (up to 99) to make it unique.
- **Validation:** the e-mail must match an e-mail regex; the password must be 8–20 characters with at least one
  lower-case letter, one upper-case letter, one digit and one special character (`@$!%*#?&`); duplicate e-mails
  are rejected.
- The password is stored as a **`sha256_crypt`** hash (passlib), never in clear text.
- The new account starts in status `Created`.

### Account activation
- After sign-up (and again if a `Created` user tries to log in) a **time-limited signed token**
  (`itsdangerous`, 1000 s) is generated and an activation link `/user/verify/<token>` is e-mailed through the
  [messaging engine](messaging.md).
- Opening the link moves the account to `Activated`. Expired or invalid links show an error and send the user
  back to the login page.
- Account states: `Created`, `Activated`, `Deactivated`, `Deleted` (`UserStatus`).

### Login / logout
- Login by e-mail + password. Wrong e-mail and wrong password return the same generic error.
- On success the user name is stored in the Flask session and the user lands on the dashboard.
- A **permanent session** with a sliding timeout is used: `session.permanent = True` and the timer is reset on
  every request. Timeout is `sessionLifetime` (minutes) in `config/server.json` (default 30).
- Logged-in users who open `/user/login` or `/user/signup` are redirected to the dashboard.

### Password change (logged in)
- Requires the old password, a new password and its confirmation.
- Rejects: wrong old password, mismatching confirmation, new password equal to old, and passwords that do not
  meet the strength rule above.

### Password reset (forgot password)
- `/user/password_reset_request`: enter the registered e-mail; a signed reset link is e-mailed (nothing is
  revealed if the e-mail is unknown).
- `/user/password_reset/<token>`: validates the token, then lets the user set a new password.

### Profile
- View and edit first/middle/last name and address lines; only fields that actually changed are written.
- **Profile picture upload:** saved under `static/profile_pic/` with a random hex file name and shrunk to a
  125×125 thumbnail (Pillow). A default picture is shown when none is set.

## Endpoints

| Route | Methods | Purpose |
|---|---|---|
| `/user/signup` | GET, POST | Registration |
| `/user/verify/<token>` | GET | Activate account |
| `/user/login` | GET, POST | Login |
| `/user/logout` | GET | Logout |
| `/user/password_change` | GET, POST | Change password |
| `/user/password_reset_request` | GET, POST | Ask for a reset link |
| `/user/password_reset/<token>` | GET, POST | Set a new password |
| `/user/profile` | GET, POST | View / update profile |

## Related tables
`algo_trader.users` — see [Database](database.md).
