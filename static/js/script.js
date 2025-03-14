$(document).ready(function () {
    let cropper;
    const maxFileSize = 10 * 1024 * 1024; // 10MB
    let cropModal;

    // 初始化模态窗口
    cropModal = new bootstrap.Modal(document.getElementById('cropModal'));

    // 模态窗口关闭时销毁裁剪器
    document.getElementById('cropModal').addEventListener('hidden.bs.modal', function () {
        if (cropper) {
            cropper.destroy();
            cropper = null;
        }
    });

    // 检查文件大小并启动裁剪
    $('#photo-upload').change(function () {
        const file = this.files[0];
        if (!file) {
            return;
        }

        // 检查文件大小
        if (file.size > maxFileSize) {
            $('#file-error').removeClass('d-none');
            this.value = ''; // 清空文件选择
            return;
        }

        $('#file-error').addClass('d-none');

        // 读取文件并显示模态窗口
        const reader = new FileReader();
        reader.onload = function (e) {
            // 设置图片源
            $('#crop-image').attr('src', e.target.result);

            // 显示裁剪模态窗口
            cropModal.show();

            // 延迟初始化裁剪器，确保图片加载完成并且模态窗口已显示
            setTimeout(initCropper, 300);
        };
        reader.readAsDataURL(file);
    });

    // 初始化裁剪器
    function initCropper() {
        // 如果已存在裁剪实例，先销毁
        if (cropper) {
            cropper.destroy();
        }

        // 创建新的裁剪实例
        const image = document.getElementById('crop-image');
        cropper = new Cropper(image, {
            aspectRatio: 3 / 4,
            viewMode: 1,
            dragMode: 'move',
            autoCropArea: 0.8,
            restore: false,
            guides: true,
            center: true,
            highlight: false,
            cropBoxMovable: true,
            cropBoxResizable: true,
            toggleDragModeOnDblclick: false,
            preview: '#preview-box',
            ready: function () {
                // 确保裁剪框完全可见
                const containerData = cropper.getContainerData();
                const canvasData = cropper.getCanvasData();
                const cropBoxData = cropper.getCropBoxData();

                // 调整缩放以确保裁剪框完全显示
                if (cropBoxData.width > containerData.width ||
                    cropBoxData.height > containerData.height) {
                    const scale = Math.min(
                        containerData.width / cropBoxData.width,
                        containerData.height / cropBoxData.height
                    ) * 0.9; // 缩小10%以确保有边距

                    cropper.zoomTo(scale);
                }
            }
        });
    }

    // 旋转按钮
    $('#rotate-btn').click(function () {
        if (cropper) {
            cropper.rotate(90);
        }
    });

    // 确认裁剪
    $('#confirm-crop').click(function () {
        if (cropper) {
            // 获取裁剪后的canvas
            const canvas = cropper.getCroppedCanvas({
                width: 120,
                height: 160,
                imageSmoothingEnabled: true,
                imageSmoothingQuality: 'high'
            });

            // 转换为base64
            const croppedImageData = canvas.toDataURL('image/jpeg', 0.92);

            // 显示预览
            $('#photo-preview').attr('src', croppedImageData);
            $('#photo-preview-container').removeClass('d-none');

            // 存储裁剪后的图片数据
            $('#cropped-data').val(croppedImageData);

            // 关闭模态窗口
            cropModal.hide();
        }
    });

    // 更换照片
    $('#change-photo').click(function () {
        $('#photo-preview-container').addClass('d-none');
        $('#photo-upload').val('').click();
    });

    // 表单提交逻辑
    $('#resume-form').submit(function (e) {
        e.preventDefault();

        // 显示加载状态
        $('#generate-btn').prop('disabled', true);
        $('#loading-spinner').removeClass('d-none');
        $('#btn-text').text('生成中...');
        $('#error-alert').addClass('d-none');
        $('#result-section').addClass('d-none');

        // 收集表单数据
        let formData = new FormData(this);

        // 发送AJAX请求
        $.ajax({
            url: '/generate',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                if (response.success) {
                    // 成功生成简历
                    $('#preview-link').attr('href', response.file_url);
                    $('#download-link').attr('href', response.file_url);
                    $('#download-link').attr('download', response.filename);
                    $('#result-section').removeClass('d-none');

                    // 滚动到结果区域
                    $('html, body').animate({
                        scrollTop: $('#result-section').offset().top - 100
                    }, 500);
                } else {
                    // 显示错误
                    $('#error-message').text(response.error || '简历生成失败，请重试');
                    $('#error-alert').removeClass('d-none');
                }
            },
            error: function (xhr) {
                // 处理错误
                let errorMessage = '服务器错误，请稍后重试';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMessage = xhr.responseJSON.error;
                }
                $('#error-message').text(errorMessage);
                $('#error-alert').removeClass('d-none');
            },
            complete: function () {
                // 恢复按钮状态
                $('#generate-btn').prop('disabled', false);
                $('#loading-spinner').addClass('d-none');
                $('#btn-text').text('生成简历');
            }
        });
    });
});