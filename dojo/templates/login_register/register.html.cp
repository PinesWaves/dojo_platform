{% load static %}
{% load custom_filters %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Seishin JKA Dojo | Registration Page</title>

  <!-- Google Font: Source Sans Pro -->
  <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Source+Sans+Pro:300,400,400i,700&display=fallback">
  <!-- Font Awesome -->
  <link rel="stylesheet" href="{% static 'plugins/fontawesome-free/css/all.min.css' %}">
  <!-- Tempus Dominus Bootstrap 4 CSS - For datepicker -->
  <link rel="stylesheet" href="{% static 'plugins/tempusdominus-bootstrap-4/css/tempusdominus-bootstrap-4.min.css' %}">
  <!-- Country picker flags -->
  <link rel="stylesheet" href="{% static 'plugins/bootstrap-select-country-4.2.0/css/bootstrap-select-country.min.css' %}">
  <!-- icheck bootstrap -->
  <link rel="stylesheet" href="{% static 'plugins/icheck-bootstrap/icheck-bootstrap.min.css' %}">
  <!-- Theme style -->
  <link rel="stylesheet" href="{% static 'dist/css/adminlte.min.css' %}">
  <link rel="icon" href="{% static 'img/icon.png' %}">

  <style>
    .dropdown-toggle.btn-default {
      color: #292b2c;
      background-color: #fff;
      border-color: #ccc;
    }
    .bootstrap-select.show > .dropdown-menu > .dropdown-menu {
      display: block;
    }
    .bootstrap-select > .dropdown-menu > .dropdown-menu li.hidden {
      display: none;
    }
    .bootstrap-select > .dropdown-menu > .dropdown-menu li a {
      display: block;
      width: 100%;
      padding: 3px 1.5rem;
      clear: both;
      font-weight: 400;
      color: #292b2c;
      text-align: inherit;
      white-space: nowrap;
      background: 0 0;
      border: 0;
      text-decoration: none;
    }
    .bootstrap-select > .dropdown-menu > .dropdown-menu li a:hover {
      background-color: #f4f4f4;
    }
    .bootstrap-select > .dropdown-toggle {
      width: 100%;
    }
    .dropdown-menu > li.active > a {
      color: #fff !important;
      background-color: #337ab7 !important;
    }
    .bootstrap-select .check-mark {
      line-height: 14px;
    }
    .bootstrap-select .check-mark::after {
      font-family: "FontAwesome", serif;
      content: "\f00c";
    }
    .bootstrap-select button {
      overflow: hidden;
      text-overflow: ellipsis;
    }

    /* Make filled out selects be the same size as empty selects */
    .bootstrap-select.btn-group .dropdown-toggle .filter-option {
      display: inline !important;
    }
  </style>
</head>
<body class="dark-mode hold-transition register-page">
<div class="register-box">
  <div class="register-logo">
    <a href="{% url 'login' %}">
      <img src="{% static 'img/banner.png' %}" alt="">
    </a>
  </div>

  <div class="card">
    <div class="card-body card-danger card-outline register-card-body">
      <p class="login-box-msg">Register a new membership</p>
      <form id="registration_form" method="post" action="{% url 'signup' token %}">
        {% csrf_token %}
        <div class="tab-content" id="registration-tabContent">
          {% csrf_token %}
          <div class="progress mb-3">
            <div class="progress-bar bg-danger" role="progressbar" aria-valuenow="1" aria-valuemin="1"
                 aria-valuemax="{{ sectioned_fields|length }}" style="width: 20%">
            </div>
          </div>
          {% for section_num, fields in sectioned_fields %}
            <div class="tab-pane fade {% if section_num == 1 %}show active{% endif %}"
                 id="section-{{ section_num }}"
                 role="tabpanel"
                 aria-labelledby="section-{{ section_num }}-tab"
                 data-section="{{ section_num }}">

              {% for field in fields %}
                <div class="form-group">
                  {% if field|widget_type != "custom" %}
                    <label for="{{ field.id_for_label }}">{{ field.label }}</label>
                  {% endif %}
                  {{ field }}
                  {% if field.errors %}
                    <div class="invalid-feedback">
                      {% for error in field.errors %}
                        <p>{{ error }}</p>
                      {% endfor %}
                    </div>
                  {% endif %}
                </div>
              {% endfor %}
              <div class="form-group">
                {% if section_num == sectioned_fields|length %}
                  <button type="button" class="btn btn-danger prev-btn" data-prev="{{ section_num }}"><i
                      class="fas fa-chevron-left"></i></button>
                  <button type="submit" class="btn btn-danger float-right">Register</button>
                {% elif section_num == 1 %}
                  <button type="button" class="btn btn-danger next-btn float-right" data-next="{{ section_num }}"><i
                      class="fas fa-chevron-right"></i></button>
                {% else %}
                  <button type="button" class="btn btn-danger prev-btn" data-prev="{{ section_num }}"><i
                      class="fas fa-chevron-left"></i></button>
                  <button type="button" class="btn btn-danger next-btn float-right" data-next="{{ section_num }}"><i
                      class="fas fa-chevron-right"></i></button>
                {% endif %}
              </div>
            </div>
          {% endfor %}
        </div>
      </form>
      <br>
    </div>
    <a href="{% url 'login' %}" class="text-center">I already have a membership</a>
    <br>
     <!--/.form-box -->
  </div><!-- /.card -->
</div>
<!-- /.register-box -->

<!-- jQuery -->
<script src="{% static 'plugins/jquery/jquery.min.js' %}"></script>
<!-- jquery-validation -->
<script src="{% static 'plugins/jquery-validation/jquery.validate.min.js' %}"></script>
<script src="{% static 'plugins/jquery-validation/additional-methods.min.js' %}"></script>
<!-- Bootstrap 4 -->
<script src="{% static 'plugins/bootstrap/js/bootstrap.bundle.min.js' %}"></script>
<!-- Tempusdominus Bootstrap 4 -->
<script src="{% static 'plugins/moment/moment.min.js' %}"></script>
<!-- For datepicker -->
<script src="{% static 'plugins/tempusdominus-bootstrap-4/js/tempusdominus-bootstrap-4.min.js' %}"></script>
<!-- AdminLTE App -->
<script src="{% static 'dist/js/adminlte.min.js' %}"></script>
<!-- Country picker flags -->
<script src="{% static 'plugins/bootstrap-select-country-4.2.0/js/bootstrap-select-country.min.js' %}"></script>
<script>
    $(document).ready(function () {
        $(".next-btn").click(function () {
            var currentSection = $(this).data("next");
            var nextSection = currentSection + 1;
            $(".progress-bar").attr("aria-valuenow", nextSection);
            $(".progress-bar").attr("style", "width:" + nextSection * 100 / $(".progress-bar").attr("aria-valuemax") + "%");

            // Hide current tab and show next tab
            $("#section-" + currentSection).removeClass("show active");
            $("#section-" + nextSection).addClass("show active");
        });

        $(".prev-btn").click(function () {
            var currentSection = $(this).data("prev");
            var prevSection = currentSection - 1;
            $(".progress-bar").attr("aria-valuenow", prevSection);
            $(".progress-bar").attr("style", "width:" + prevSection * 100 / $(".progress-bar").attr("aria-valuemax") + "%");

            // Hide current tab and show previous tab
            $("#section-" + currentSection).removeClass("show active");
            $("#section-" + prevSection).addClass("show active");
        });

        $('#id_birth_date').datetimepicker({
            format: 'L'
        });

        $('#id_date_joined').datetimepicker({
            format: 'L'
        });

        $('.countrypicker').countrypicker();

        //$.validator.setDefaults({
        //    submitHandler: function () {
        //        alert("Form successful submitted!");
        //    }
        //});

        $('#registration_form').validate({
            rules: {
                first_name: { required: true },
                last_name: { required: true },
                id_type: { required: true },
                id_number: { required: true },
                gender: { required: true },
                birth_date: { required: true, date: true },
                birth_place: { required: true },
                profession: { required: true },
                email: { required: true, email: true },
                phone_number: { required: true, digits: true },
                country: { required: true },
                city: { required: true },
                address: { required: true },
                parent: { required: true },
                parent_phone_number: { required: true, digits: true },
                password1: { required: true, minlength: 8 },
                password2: {
                    required: true,
                    equalTo: "#id_password1"
                },
                eps: { required: true },
                date_joined: { required: true, date: true },
                physical_cond: { required: true },
                medical_cond: { required: true },
                drug_cons: { required: true },
                allergies: { required: true },
                other_activities: { required: true },
                cardio_prob: { required: false },
                injuries: { required: false },
                physical_limit: { required: false },
                lost_cons: { required: false },
                sec_recom: { required: true },
                agreement: { required: true }
            },
            messages: {
                first_name: "Please enter your first name",
                last_name: "Please enter your last name",
                email: "Enter a valid email address",
                password2: "Passwords must match",
                phone_number: "Enter a valid phone number",
                parent_phone_number: "Enter a valid phone number"
                // Puedes personalizar más mensajes si lo deseas
            },
            errorClass: "is-invalid",
            validClass: "",
            errorElement: "div",
            errorPlacement: function (error, element) {
                error.addClass('invalid-feedback');
                element.closest('.form-group').append(error);
            },
            /*highlight: function (element) {
                $(element).addClass("is-invalid");
            },
            unhighlight: function (element) {
                $(element).removeClass("is-invalid");
            }*/
        });
    });
</script>
</body>
</html>
