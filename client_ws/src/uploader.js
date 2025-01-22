import fs from "fs";
import path from 'path';
import fetch from "node-fetch";

// class Uploader {
//     constructor(file, onProgress){
//         this._file = file;
//         this._onProgress = onProgress;

//         // create fileId that uniquely identifies the file
//         // we could also add user session identifier (if had one), to make it even more unique
//         this._fileId = file.name + '-' + file.size;
//     };

//     async getUploadedProgress() {
//         const url = 'http://172.27.0.4:3000/v1/file/upload/progress';

//         const response = await fetch(`${url}?file_id=123`, {
//             method: "GET",
//             headers: {"Content-Type": "application/json"}
//           }
//         );

//         if (response.status != 200){
//             throw new Error(`Failed get uploaded bytes`);
//         }

//         const resp = await response.json();

//         return resp.started_bytes;
//     }

//     async upload(formData) {

//         const url = "http://172.27.0.4:3000/v1/file/upload";

//         try {


//             const response = await fetch(url, {
//                 method: 'POST',
//                 body: JSON.stringify(body),
//                 headers: {'Content-Type': 'application/json'}
//             });

//             console.log(await response.json());

//         } catch(err) {
//             console.error(`Failed to upload: ${err.message}`);
//         }

//     }


// }


const uploadFile = async (filePath, fileId) => {

    try {
        // Stream the remaining part of the file
        const fileStream = fs.createReadStream(filePath, { start: 0 });
        const response = await fetch('http://172.27.0.4:3000/v1/file/upload', {
          method: 'POST',
          headers: {
            'x-file-id': fileId,
            'x-file-name': path.basename(filePath),
            'x-start-byte': 0,
            'Content-Type': 'application/octet-stream',
          },
          body: fileStream,
        });

        console.log(await response.json());

    } catch (error) {
        console.error('Error uploading file:', error);
    }

}

const getUploadedProgress = async(fileId) => {
  try{
    const response = await fetch(`http://172.27.0.4:3000/v1/file/upload/progress?file_id=${fileId}`, {
      method: 'GET',
      headers: {'Content-Type': 'application/json'}
    });

    console.log(await response.json());

  } catch(error){
    console.error('Error getting uploaded progress:', error);
  }
}


uploadFile("/home/chunwei/src/test", "123456");

setTimeout(() => {
  getUploadedProgress("123456");
}, 2000);

setTimeout(() => {
  getUploadedProgress("123456");
}, 5000);


// const uploader = new Uploader();
// uploader.upload(formData)
// uploader.getUploadedProgress();