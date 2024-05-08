function onScanSuccess(decodedText, decodedResult) {
    document.querySelector('[data-reader-input="1"]').value = decodedText;
    document.querySelector('[data-reader-input="1"]').parentElement.submit();
}

let config = {
    fps: 10,
    rememberLastUsedCamera: true,
    // Only support camera scan type.
    supportedScanTypes: [Html5QrcodeScanType.SCAN_TYPE_CAMERA]
};

let html5QrcodeScanner = new Html5QrcodeScanner(
    document.querySelector('[data-reader-scanner="1"]').id,
    config,
    false);
html5QrcodeScanner.render(onScanSuccess);