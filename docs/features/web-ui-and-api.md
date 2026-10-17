# Web UI and HTTP endpoints

The UI is server-rendered Flask + Jinja2. Every endpoint is a class-based view (`MethodView`) registered in
`src/app/endpoints.py`. Most views follow the same pattern: check `g.user` (set from the session in the
`before_request` hook), call a `*Methods` service class, then `flash()` a message and redirect, or return JSON.

## Pages and routes

| Route | Methods | Auth | Description | Doc |
|---|---|---|---|---|
| `/` | GET | – | Landing page | |
| `/about` | GET | – | About us | |
| `/dashboard` | GET | ✔ | Main dashboard; start/stop controls | [Algo control](algo-control.md) |
| `/user/signup` | GET, POST | – | Register | [Users](user-management.md) |
| `/user/verify/<token>` | GET | – | Activate account | [Users](user-management.md) |
| `/user/login` | GET, POST | – | Login | [Users](user-management.md) |
| `/user/logout` | GET | – | Logout (clears the session, then redirects to `/brokers`) | [Users](user-management.md) |
| `/user/profile` | GET, POST | ✔ | Profile + picture | [Users](user-management.md) |
| `/user/password_change` | GET, POST | ✔ | Change password | [Users](user-management.md) |
| `/user/password_reset_request` | GET, POST | – | Request reset link | [Users](user-management.md) |
| `/user/password_reset/<token>` | GET, POST | – | Reset password | [Users](user-management.md) |
| `/brokers` | GET | ✔ | My brokers | [Brokers](broker-management.md) |
| `/broker/add` | GET, POST | ✔ | Add broker | [Brokers](broker-management.md) |
| `/broker/login` | GET, POST | ✔ | Broker login | [Brokers](broker-management.md) |
| `/broker/logout` | GET | – | Broker logout | [Brokers](broker-management.md) |
| `/broker/enquire/<broker_id>` | GET | – | Broker enquiry page | [Brokers](broker-management.md) |
| `/strategies` | GET | ✔ | My strategies | [Strategies](strategies.md) |
| `/api/<page_name>` | GET | – | Renders `orders`, `positions` or `holdings` pages (other names flash an error and show the dashboard) | [Brokers](broker-management.md) |

## JSON endpoints

| Route | Response |
|---|---|
| `/algo/start` | `{status: "success"\|"fail", message}` |
| `/algo/stop` | `{status, message}` |
| `/algo/status` | `{status, algoStatus: "Running"\|"Stopped"}` |
| `/oms/orders` | `{status, data: [orders…]}` |
| `/oms/positions` | `{status, data: {net, day}}` |
| `/oms/holdings` | `{status, data: [holdings…]}` |

On failure the JSON carries a user-readable `message`; for the algo endpoints no stack trace is exposed.

## Request lifecycle hooks (`app/app.py`)

- `before_first_request` → [bootup operations](algo-control.md#start-up-reset).
- `before_request` → makes the session permanent and refreshes it, copies `session['user']` into `g.user`,
  opens the PostgreSQL handle in `g.db`.
- `teardown_appcontext` → releases `g.db`.

## Templates (`src/templates/`)

| Template | Purpose |
|---|---|
| `layout.html`, `navbar.html`, `flash.html` | Shared shell, navigation and flash-message partial |
| `index.html`, `about_us.html`, `dashboard.html` | Landing, about, dashboard |
| `signup.html`, `login.html`, `profile.html`, `change_password.html`, `reset_request.html`, `reset_password.html` | User pages |
| `my_brokers.html`, `add_broker.html`, `login_broker.html`, `broker.html` | Broker pages |
| `orders.html`, `positions.html`, `holdings.html` | Account data views |
| `strategies.html` | Strategy list |
| `400/403/404/405/500.html` | Error pages |

Styling is in `src/static/main.css`; uploaded profile pictures go to `src/static/profile_pic/`.

## Forms (`src/forms/`)

Flask-WTF forms with server-side validators: `RegisterUserForm`, `LoginForm`, `UpdateAccountForm`,
`ChangePasswordForm`, `RequestResetForm`, `ResetPasswordForm`, `BrokerCreateForm`, `BrokerEnquiryForm`,
`BrokerLoginForm`. CSRF protection comes from Flask-WTF.
