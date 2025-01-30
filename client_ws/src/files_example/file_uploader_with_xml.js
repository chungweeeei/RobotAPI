const fs = require('fs');
const path = require('path');
const { start } = require('repl');
const XMLHttpRequest = require('xmlhttprequest').XMLHttpRequest;

const fileBaseURL = "http://172.27.0.4:3000/v1/file";
const uploadURL = `${fileBaseURL}/upload`;
const fetchUploadProgressURL= `${fileBaseURL}/upload/progress`;

// const xhr = new XMLHttpRequest();

// /*
//     xhr.open(method, URL, [async, user, password])
//     This method specifies the main parameters of thee request:
//     - method: the HTTP method to use when making the request.
//     - URL: the URL to make the request to.
//     - async: a boolean value that determines whether the request should be handled asynchronously or not.
//     - user, password: login and password for basic HTTP auth (if required).
// */

// // Please note that open call does not open the connection. It only configures
// // the request, but the network activity only starts with the send call.

// xhr.open('GET', `${fileBaseURL}`, true);

// /*
//     Ready states

//     XMLHttpRequest changes between states as it progresses. The current state is accessible as xhr.readyState.
//     All states are:
//     - 0: UNSENT: initial state
//     - 1: OPENED: open called
//     - 2: HEADERS_RECEIVED: response headers received
//     - 3: LOADING: response is loading (a data packet is received)
//     - 4: DONE: The operation is complete.
// */

// xhr.onreadystatechange = function () {
//     if (xhr.readyState === 4){
//         const response = JSON.parse(xhr.responseText);
//         console.log(response);
//     }
// };

// // This method opens the connection and sends the request to the server. The optional body
// // parameter contains the request body.

// xhr.send();

// In a Node.js environment, you can't use the XMLHttpRequest object directly since it is a browser-specific API.


class uploader {
    constructor (filePath, fileId){
        this._filePath = filePath;
        this._fileId = fileId;
    }

    async getUploadedProgress() {
        return new Promise((resolve, reject) => {
            try {
                const xhr = new XMLHttpRequest();
                xhr.open('GET', `${fetchUploadProgressURL}?file_id=${this._fileId}`, true);

                xhr.onreadystatechange = function () {
                    if (xhr.readyState === 4){
                        if (xhr.status == 200){
                            const response = JSON.parse(xhr.responseText);
                            resolve(response.uploaded_byte);
                        } else {
                            reject(`Error: ${xhr.statusText}`);
                        }
                    }
                };

                xhr.send();

            } catch (error){
                console.error("Error getting uploaded progress:", error);
                reject(error);
            }
        })
    }

    async uploadFile() {

        try {
            const startByte = await this.getUploadedProgress();

            // register xhr instance
            const xhr = this._xhr = new XMLHttpRequest()

            xhr.open("POST", uploadURL, true);

            // set request header
            xhr.setRequestHeader("x-file-id", this._fileId);
            xhr.setRequestHeader('x-file-name', path.basename(this._filePath));
            xhr.setRequestHeader('x-start-byte', startByte);
            xhr.setRequestHeader("Content-Type", "application/octet-stream");

            xhr.onreadystatechange = function () {
                if(xhr.readyState === 4){
                    // handle status code
                    console.log(`Receive response from api server, status: ${xhr.status}`);
                } else {
                    console.log(`Current state: ${xhr.readyState}`);
                }
            }

            // read file
            fs.readFile(this._filePath, (err, data) => {
                if (err){
                    throw new Error(`Failed to Read ${this._filePath}`)
                }

                console.log(`[UpLoader][uploadFile] Finished read file ${this._filePath}`);

                xhr.send(data.slice(this.startByte));
            })


        } catch (error){
            console.error(`Failed to upload file: ${error}`);
        }

    }

    async stopUpload() {
        if (this._xhr){
            this._xhr.abort()
        }
    }
}

const testLoader = new uploader('/home/chunwei/src/app_log.tar.gz', '123456');

testLoader.uploadFile();

// const testResumable = async () => {

//   // Start upload
//   testLoader.uploadFile();

//   // Stop upload after 5 seconds
//   setTimeout(async () => {
//       console.log("Stopping upload...");
//       testLoader.stopUpload();

//       setTimeout(async () => {
//         console.log("Restart sending Test endpoint");
//         testLoader.uploadFile();
//       }, 5000)

//   }, 300);
// };

// testResumable();