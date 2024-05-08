function onScanSuccess(decodedText, decodedResult) {
    // handle the scanned code as you like, for example:
    console.log(`Code matched = ${decodedText}`, decodedResult);
}

let config = {
    fps: 10,
    qrbox: { width: 100, height: 100 },
    rememberLastUsedCamera: true,
    // Only support camera scan type.
    supportedScanTypes: [Html5QrcodeScanType.SCAN_TYPE_CAMERA]
};

let html5QrcodeScanner = new Html5QrcodeScanner(
    "reader", config, /* verbose= */ false);
html5QrcodeScanner.render(onScanSuccess);