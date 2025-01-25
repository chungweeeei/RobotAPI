import fs from "fs";
import path from 'path';
import fetch from "node-fetch";

const fileBaseURL = "http://172.27.0.4:3000/v1/file";
const uploadURL = `${fileBaseURL}/upload`;
const fetchUploadProgressURL= `${fileBaseURL}/upload/progress`;

class uploader {

    constructor (filePath, fileId){
      this._filePath = filePath;
      this._fileId = fileId;
    }

    async getUploadedProgress(){
      try{
        const response = await fetch(`${fetchUploadProgressURL}?file_id=${this._fileId}`, {
          method: 'GET',
          headers: {'Content-Type': 'application/json'}
        });

        const result = await response.json();
        console.log(result);
        return result.uploaded_byte;

      } catch(error){
        console.error('Error getting uploaded progress:', error);
      }
    }

    async uploadFile(){

      try {

          const start_byte = await this.getUploadedProgress();

          // Stream the remaining part of the file
          const fileStream = this._fileStream = fs.createReadStream(this._filePath, { start: start_byte });
          const response = await fetch(`${uploadURL}`, {
            method: 'POST',
            headers: {
              'x-file-id': this._fileId,
              'x-file-name': path.basename(this._filePath),
              'x-start-byte': start_byte,
              'Content-Type': 'application/octet-stream',
            },
            body: this._fileStream,
          });

          console.log(await response.json());

      } catch (error) {
          console.error(`Error uploading file: ${error}`);
      }
    }

    async stopUpload(){
      if (this._fileStream) {
          this._fileStream.destroy();
          console.log('File upload stopped.');
      } else {
          console.log('No active file upload to stop.');
      }
    }
}


const testLoader = new uploader('/home/chunwei/src/app_log.tar.gz', '123456');

const testResumable = async () => {

  // Start upload
  testLoader.uploadFile();

  // Stop upload after 5 seconds
  setTimeout(async () => {
      console.log("Stopping upload...");
      testLoader.stopUpload();

      // Resume upload after 1 seconds
      setTimeout(async () => {
          console.log("Resuming upload...");
          testLoader.uploadFile();
      }, 5000);
  }, 300);

};

testResumable();