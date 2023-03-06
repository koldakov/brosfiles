class File {
  constructor(form) {
    this.form = form;

    this.csrfMiddlewareToken = $(this.form).find("input[name='csrfmiddlewaretoken']").val();
    this.maxFileSize = $(this.form).find("input[name='max_file_size']").val();
    this.fileInput = $(this.form).find("input[type='file']")[0];
    this.fileUploadButton = $(this.form).find("#file-upload-button");

    // Support 1 file only.
    this.file = this.fileInput.files[0];
    this.uploadURL = "";

    if (this.file.size > this.maxFileSize) {
      this.toggleUploadForm();
      throw new Error("File is too large.");
    }
  }

  toggleUploadForm() {
    let isDisabled = !$(this.form).prop("disabled");

    $(this.form).prop("disabled", isDisabled);
    $(this.form).find("input, button").prop("disabled", isDisabled);
  }

  upload() {
    this.toggleUploadForm();
    this.URLUpload();
  }

  dUpload(res) {
    let headers = res.request_data.headers;
    let token = res.token;
    let _this = this;
    let formData = new FormData();
    let body = res.request_data.body;
    let settings = {}

    // MAGIC: For some reason key must be the first argument
    for (var key in body) {
      if (body.hasOwnProperty(key)) {
        formData.append(key, body[key]);
      }
    }

    formData.append("file", _this.file, _this.file.name);

    settings = {
      "url": res.request_data.url,
      "method": res.request_data.method,
      "timeout": 0,
      "processData": false,
      "mimeType": "multipart/form-data",
      "contentType": false,
      "data": formData
    };

    $.ajax(settings)
    .done(function (data, textStatus, jqXHR) {
      if (jqXHR.status === 204) {
        _this.finishURLUpload(token);
      } else {
        console.error(textStatus);
        _this.toggleUploadForm();
      }
    })
    .fail(function (jqXHR, textStatus, errorThrown) {
      console.error(textStatus);
      _this.toggleUploadForm();
    });
  }

  finishURLUpload(token) {
    let headers = {
        "X-Transfer-Type": "SIGNED_URL",
        "X-CSRFToken": this.csrfMiddlewareToken,
        "X-Upload-Action": "FINISH",
        "X-Upload-Signature": token,
    }
    let _this = this;

    $.ajax({
      url: _this.uploadURL,
      type: "POST",
      datatype: "json",
      headers: headers,
    })
    .done(function (data) {
      window.location.href = data.redirect_url;
    })
    .fail(function (jqXHR, textStatus, errorThrown) {
      console.error(textStatus);
      _this.toggleUploadForm();
    });
  }

  URLUpload() {
    let headers = {
        "X-Transfer-Type": "SIGNED_URL",
        "X-CSRFToken": this.csrfMiddlewareToken,
        "X-Upload-Action": "START",
        "X-Signed-URL-request": this.csrfMiddlewareToken,
    }
    let _this = this;

    $.ajax({
      url: _this.uploadURL,
      type: "POST",
      datatype: "json",
      headers: headers,
      data: {
        filename: _this.file.name,
        is_private: $(this.form).find("input[name='is_private']").is(':checked')
      },
    })
    .done(function (res) {
      _this.dUpload(res);
    })
    .fail(function (jqXHR, textStatus, errorThrown) {
      console.error(textStatus);
      _this.toggleUploadForm();
    });
  }
}

$(document).ready(function() {
  $("#file-upload-form").submit(function(event) {
    event.preventDefault();

    try {
      let file = new File(event.target);
      file.upload();
    } catch(e) {
      console.error(e);
      alert(e);
      return;
    }
  });
});
