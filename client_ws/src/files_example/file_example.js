import fs, { write } from "fs";
import YAML from "js-yaml";

function readJSONFile(filePath){

    // async read the json file
    fs.readFile(filePath, (err, data) => {
        if (err) {
           return console.error(err);
        }

        const testInfo = JSON.parse(data);

        // list down all keys in parse object (use JS Object built-in function)
        const keys = Object.keys(testInfo);
        console.log(`Keys of testInfo object: ${keys}`);

        // check if keys in the object
        const checkKey = "robot_id";
        if (checkKey in testInfo){
            console.log(`Key ${checkKey} is in the object`);
        } else {
            console.log(`Key ${checkKey} is not in the object`);
        }
    });
}

function writeJSONFile(filePath){

    // async write the json file
    const defaultData = {
        robot_id: "robot02",
        robot_name: "robot02",
        ip: "172.27.0.4",
        port: 3000
    }

    const jsonString = JSON.stringify(defaultData, null, 4);

    fs.writeFile(filePath, jsonString, (err) => {
        if (err){
            console.error(err);
        }
        console.log("File has been written successfully");
    })
}

function readYAMLFile(filePath){

    if (!fs.existsSync(filePath)){
        console.error(`File ${filePath} does not exist`);
        return;
    }

    // async read the json file
    fs.readFile(filePath, (err, data) => {
        if (err) {
           return console.error(err);
        }

        const testInfo = YAML.load(data);

        // The Object.entries method returns an array of a given object's own enumerable string-keyed property [key, value] pairs

        for (const [key, value] of Object.entries(testInfo)){
            console.log(`${key}: ${value}`);
        }

    });
}

function writeYAMLFile(filePath){

    // async write the json file
    const defaultData = {
        system: {
            robot_id: "robot02",
            robot_name: "robot02",
            ip: "172.27.0.5",
            port: 3000
        }
    };

    const yamlString = YAML.dump(defaultData);

    fs.writeFile(filePath, yamlString, (err) => {
        if (err){
            console.error(err);
        }
        console.log("File has been written successfully");
    });
}


function deleteFile(filePath){
    // async delete the file
    fs.unlink(filePath, (err) => {
        if (err){
            console.error(err);
        }
        console.log("File has been deleted successfully");
    });
}

readJSONFile('./files/test.json');
writeJSONFile('./files/default.json');
readYAMLFile('./files/test.yaml');
writeYAMLFile('./files/default.yaml');
//deleteFile('./default.json');
