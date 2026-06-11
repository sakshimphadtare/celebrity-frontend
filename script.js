const API_URL = "https://l6lzk4fh7l.execute-api.ap-south-1.amazonaws.com/prod/detect-celebrity";

// Preview image immediately after selection
function previewImage() {

    const input = document.getElementById("imageInput");
    const preview = document.getElementById("previewImage");

    if (input.files && input.files[0]) {

        const reader = new FileReader();

        reader.onload = function (e) {

            preview.src = e.target.result;
            preview.style.display = "block";

        };

        reader.readAsDataURL(input.files[0]);
    }
}


async function uploadImage() {

    const input = document.getElementById("imageInput");
    const file = input.files[0];
    const resultBox = document.getElementById("result");

    if (!file) {

        resultBox.innerHTML = "⚠️ Please select an image first!";
        return;
    }

    resultBox.innerHTML = `
        <h3>🔄 Analyzing Image...</h3>
        <p>Please wait while AI detects the celebrity.</p>
    `;

    const reader = new FileReader();

    reader.onloadend = async function () {

        const base64Image = reader.result.split(",")[1];

        try {

            const response = await fetch(API_URL, {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    image: base64Image,
                    file_name: file.name

                })

            });

            const data = await response.json();

            console.log("API Response:", data);

            // Celebrity found
            if (data.celebrity_name) {

                const confidence = parseFloat(data.confidence).toFixed(2);

                resultBox.innerHTML = `

                    <h2>🎉 Celebrity Detected</h2>

                    <p><b>Name:</b> ${data.celebrity_name}</p>

                    <p><b>Confidence:</b> ${confidence}%</p>

                    <div style="
                        width:100%;
                        height:18px;
                        background:#1e293b;
                        border-radius:20px;
                        overflow:hidden;
                        margin-top:15px;
                    ">

                        <div style="
                            width:${confidence}%;
                            height:100%;
                            background:linear-gradient(to right,#22c55e,#3b82f6);
                        ">
                        </div>

                    </div>

                `;

            }

            else {

                resultBox.innerHTML = `
                    <h3>❌ No celebrity detected</h3>
                `;
            }

        }

        catch (error) {

            console.error(error);

            resultBox.innerHTML = `
                <h3>❌ Error calling API</h3>
            `;
        }

    };

    reader.readAsDataURL(file);
}