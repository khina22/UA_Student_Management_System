// -----------------------Form Validation--------------------------------//
const MarkSubmission = document.getElementById('info');
const markfv = FormValidation.formValidation(MarkSubmission, {
  fields: {
    class_test_1: {
      validators: {
        notEmpty: {
          message: 'This field is required',
        },
        numeric: {
          message: 'The value is not a number',
          thousandsSeparator: '',
          decimalSeparator: '.',
        },
        callback: {
          callback: function (input) {
            const fullMarks = 20; // Change this value according to your requirements
            const enteredMarks = parseFloat(input.value);
            if (enteredMarks > fullMarks) {
                return {
                  valid: false,
                  message: 'Marks entered cannot exceed the full marks',
                };
              } else {
                return {
                  valid: true,
                };
              }
          }
        }
      }
    },
    CA: {
      validators: {
        notEmpty: {
          message: 'This field is required',
        },
        numeric: {
          message: 'The value is not a number',
          thousandsSeparator: '',
          decimalSeparator: '.',
        },
        callback: {
          callback: function (input) {
            const fullMarks = 10; // Change this value according to your requirements
            const enteredMarks = parseFloat(input.value);
            if (enteredMarks > fullMarks) {
                return {
                  valid: false,
                  message: 'Marks entered cannot exceed the full marks',
                };
              } else {
                return {
                  valid: true,
                };
              }
          }
        }
      }
    },
    mid_term: {
      validators: {
        notEmpty: {
          message: 'This field is required',
        },
        numeric: {
          message: 'The value is not a number',
          thousandsSeparator: '',
          decimalSeparator: '.',
        },
        callback: {
          callback: function (input) {
            const fullMarks = 100; // Change this value according to your requirements
            const enteredMarks = parseFloat(input.value);
            if (enteredMarks > fullMarks) {
                return {
                  valid: false,
                  message: 'Marks entered cannot exceed the full marks',
                };
              } else {
                return {
                  valid: true,
                };
              }
          }
        }
      }
    },
    annual_exam: {
      validators: {
        notEmpty: {
          message: 'This field is required',
        },
        numeric: {
          message: 'The value is not a number',
          thousandsSeparator: '',
          decimalSeparator: '.',
        },
        callback: {
          callback: function (input) {
            const fullMarks = 100; // Change this value according to your requirements
            const enteredMarks = parseFloat(input.value);
            if (enteredMarks > fullMarks) {
                return {
                  valid: false,
                  message: 'Marks entered cannot exceed the full marks',
                };
              } else {
                return {
                  valid: true,
                };
              }
          }
        }
      }
    },
    class_test_2: {
      validators: {
        notEmpty: {
          message: 'This field is required',
        },
        numeric: {
          message: 'The value is not a number',
          thousandsSeparator: '',
          decimalSeparator: '.',
        },
        callback: {
          callback: function (input) {
            const fullMarks = 20; // Change this value according to your requirements
            const enteredMarks = parseFloat(input.value);
            if (enteredMarks > fullMarks) {
                return {
                  valid: false,
                  message: 'Marks entered cannot exceed the full marks',
                };
              } else {
                return {
                  valid: true,
                };
              }
          }
        }
      }
    },
    std_status: {
      validators: {
        notEmpty: {
          message: 'This field is required',
        }
      }
    },
    punctuality: {
      validators: {
        notEmpty: {
          message: 'This field is required',
        }
      }
    },
    discipline: {
      validators: {
        notEmpty: {
          message: 'This field is required',
        }
      }
    },
    socialservice: {
      validators: {
        notEmpty: {
          message: 'This field is required',
        }
      }
    },
    leadership: {
      validators: {
        notEmpty: {
          message: 'This field is required',
        }
      }
    }
  },
  plugins: {
    trigger: new FormValidation.plugins.Trigger(),
    bootstrap: new FormValidation.plugins.Bootstrap(),
    submitButton: new FormValidation.plugins.SubmitButton(),
  },
}).on('core.form.valid', function () {
  std_detail_validation();
}).on('core.form.invalid', function () {
  swal('Validation failed !!!', 'Some required fields are empty', 'error');
});
