const constraints = {
    audio: true,
    video: false
};

// Define mediaRecorder globally
if (typeof window.mediaRecorder === 'undefined') {
    window.mediaRecorder = null;
    window.audioChunks = [];
}
if (typeof window.recognition === 'undefined') {
    window.recognition = null;
}

let isRecording = !this.origin.active;


function sendAudioToServer(blob) {
    const reader = new FileReader();
    reader.readAsDataURL(blob);
    reader.onloadend = function() {
        console.log("send audio to server");
        const base64data = reader.result;
        // console.log(base64data);
        document.dispatchEvent(new CustomEvent("GET_BLOB", {detail: base64data}));

    };
    reader.onerror = function(e) {
        console.error(e);
        console.error("Error reading the file");
    };
}

const getMimeType = () => {
    const types = [
        'audio/webm;codecs=opus',
        'audio/ogg;codecs=opus',
        'audio/webm',
        'audio/mp4'
    ];
    
    for (const type of types) {
        if (MediaRecorder.isTypeSupported(type)) {
            console.log('Supported mimeType:', type);
            return type;
        }
    }
    console.error('No supported mimeType found');
    return 'audio/webm'; // 기본값
};

function startRecording() {
    if (isRecording) return;

    navigator.mediaDevices
    .getUserMedia(constraints)
    .then((stream) => {
        const codec = getMimeType();
        window.mediaRecorder = new MediaRecorder(stream, { mimeType: codec });
        
        window.recognition = new (webkitSpeechRecognition || SpeechRecognition)();
        window.recognition.lang = '%s';
        window.recognition.continuous = true;
        window.recognition.interimResults = true;
        window.recognition.maxAlternatives = 1;

        var available_to_push = false;

        window.mediaRecorder.ondataavailable = async (event) => {
            // console.log("ondataavailable called");
            if (event.data.type.startsWith('audio/')) {
                const audioUrl = URL.createObjectURL(new Blob([event.data], { type: codec } ));
                const audio = new Audio(audioUrl);
                audio.controls = true; // 재생 컨트롤 표시 (선택 사항)
                document.body.appendChild(audio); // 페이지에 추가하여 재생
                audio.oncanplay = (event) => {
                    console.log("오디오 재생 가능");
                    audio.play();
                }
                audio.onerror = (event) => {
                    console.error("오디오 재생 실패");
                    if (audio.error) {
                      console.error("MediaError 코덱에러:", audio.error.code);
                      switch (audio.error.code) {
                        case MediaError.MEDIA_ERR_ABORTED:
                          console.error("오류 원인: 사용자에 의해 가져오기 프로세스가 중단되었습니다.");
                          break;
                        case MediaError.MEDIA_ERR_NETWORK:
                          console.error("오류 원인: 오디오 리소스를 다운로드하는 동안 네트워크 오류가 발생했습니다.");
                          break;
                        case MediaError.MEDIA_ERR_DECODE:
                          console.error("오류 원인: 오디오 리소스를 디코딩하는 동안 오류가 발생했습니다.");
                          break;
                        case MediaError.MEDIA_ERR_SRC_NOT_SUPPORTED:
                          console.log(codec);
                          console.error("오류 원인: 오디오 리소스가 지원되지 않거나, 해당 미디어를 지원하는 코덱이 없습니다.");
                          break;
                        default:
                          console.error("알 수 없는 MediaError");
                          break;
                      }
                    }
                  };
              }
            if (available_to_push) {
               if (event.data.size > 0 && event.data){
                    console.log(event.data.type, event.timecode);
                    window.audioChunks.push(event.data);
               }               
            }
            // console.log(event.data);
            // console.log(window.mediaRecorder.requestData());
        };
        
        window.mediaRecorder.onstop = () => {
            const audioBlob = new Blob(window.audioChunks, { type: codec });
            // Send blob to API
            const jsonData = JSON.stringify({
                pcmfile: audioBlob,
                type: "pcm",
                language: "ko",
                initialPrompt: "",
                patient: "",
                device_id: "device"
            });
            
            const xhr = new XMLHttpRequest();
            xhr.open('POST', 'http://175.209.148.123:8000/transcribe', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.setRequestHeader('Accept', 'application/json');
            
            xhr.onload = function() {
                if (xhr.status === 200) {
                    const data = JSON.parse(xhr.responseText);
                    console.log('Success:', data);
                    // Clear chunks for next recording
                    document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: "Recording stopped"}));
                    window.audioChunks = [];                                
                }
            };
            
            xhr.onerror = function() {
                console.error('Error:', xhr.statusText);
            };
            
            // xhr.send(jsonData);
            // document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: "Recording stopped"}));
        };
        
        window.recognition.onspeechstart = () => {
            available_to_push = true;
            console.log("Speech has been detected");
        };

        window.recognition.onspeechend = () => {
            available_to_push = false;
            console.log("Speech has stopped being detected");
            var audioBlob = new Blob(window.audioChunks, { type: codec });
            sendAudioToServer(audioBlob);
        };
        
        window.recognition.onstart = () => {
            console.log("Speech recognition service has started");
        };
        
        window.recognition.onend = () => {
            console.log("Speech recognition service has ended");
            if (window.mediaRecorder.state != 'inactive'){
                window.recognition.start();
            };
        };

        window.recognition.onsoundstart = () => {
            console.log("Some sound is being received");
        };

        window.recognition.onsoundend = () => {
            console.log("Sound has stopped being received");
        };

        window.recognition.onnomatch = () => {
            console.error("Speech not recognized");
        };

        window.recognition.onaudiostart = () => {
            console.log("Audio capturing started");
        };

        window.recognition.onaudioend = () => {
            console.log("Audio capturing ended");
        };

        window.recognition.onresult = (e) => {
            console.log("onresult called");
            var value = "";
            for (var i = e.resultIndex; i < e.results.length; ++i) {
                console.log(e.results[i])
                if (e.results[i].isFinal) {
                    value += e.results[i][0].transcript;
                    console.log(value);
                }
            }
            if (value != "") {
                document.dispatchEvent(new CustomEvent("GOOGLE_STT", {detail: value}));
                
                var audioBlob = new Blob(window.audioChunks, { type: codec });
                sendAudioToServer(audioBlob);
            }
        };

        // Start recording in 100ms chunks
        window.mediaRecorder.start(100);
        window.recognition.start();
        isRecording = true;
        console.log("Recording started");
    })
    .catch((err) => {
        console.error("Error accessing media devices:", err);
    });
}

function stopRecording() {
    console.log("stopRecording called")
    if (!isRecording) return;
    
    if (window.mediaRecorder && window.mediaRecorder.state != 'inactive') {
        isRecording = false;
        window.mediaRecorder.stop();
        window.recognition.stop();
                
        // Stop all tracks in the stream
        window.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        console.log("Recording stopped");
    }
}

// Toggle recording state when button is clicked
if (isRecording) {
    console.log("stopRecording called");
    stopRecording();
    this.origin.label = "Start";
    document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: "Recording stopped"}));
} else {
    console.log("startRecording called");
    startRecording();
    this.origin.label = "Stop";
    document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: "Recording started"}));
}