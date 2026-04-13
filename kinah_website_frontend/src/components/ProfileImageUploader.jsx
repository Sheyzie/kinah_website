// import React, { useRef, useState } from "react";
// import "./ProfileImageUploader.css";

// export default function ProfileImageUploader({ initialImage, onChange }) {
//   const [image, setImage] = useState(initialImage || null);
//   const [dragActive, setDragActive] = useState(false);
//   const fileInputRef = useRef(null);

//   const handleFile = (file) => {
//     if (!file || !file.type.startsWith("image/")) return;

//     const preview = URL.createObjectURL(file);
//     setImage(preview);

//     if (onChange) {
//       onChange(file);
//     }
//   };

//   const handleInputChange = (e) => {
//     const file = e.target.files[0];
//     handleFile(file);
//   };

//   const handleDrop = (e) => {
//     e.preventDefault();
//     setDragActive(false);

//     const file = e.dataTransfer.files[0];
//     handleFile(file);
//   };

//   const handleDragOver = (e) => {
//     e.preventDefault();
//     setDragActive(true);
//   };

//   const handleDragLeave = () => {
//     setDragActive(false);
//   };

//   return (
//     <div
//       className={`profile-container ${dragActive ? "drag-active" : ""}`}
//       onDrop={handleDrop}
//       onDragOver={handleDragOver}
//       onDragLeave={handleDragLeave}
//     >
//       <img
//         src={image || "https://via.placeholder.com/150"}
//         alt="Profile"
//         className="profile-image"
//       />

//       <button
//         className="upload-button"
//         onClick={() => fileInputRef.current.click()}
//       >
//         📷
//       </button>

//       <input
//         type="file"
//         accept="image/*"
//         ref={fileInputRef}
//         onChange={handleInputChange}
//         hidden
//       />
//     </div>
//   );
// }

import React, { useRef, useState } from "react";
import "./ProfileImageUploader.css";

export default function ProfileImageUploader({ image, setImage, onUpload, fileRef }) {
  const [progress, setProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const simulateUpload = (file) => {
    setUploading(true);
    setProgress(0);

    let value = 0;

    const interval = setInterval(() => {
      value += 10;
      setProgress(value);

      if (value >= 100) {
        clearInterval(interval);
        setUploading(false);

        if (onUpload) {
          onUpload(file);
        }
      }
    }, 200);
  };

  const handleFile = (file) => {
    if (!file || !file.type.startsWith("image/")) return;

    const preview = URL.createObjectURL(file);
    setImage(preview);

    simulateUpload(file);
  };

  const handleInputChange = (e) => {
    handleFile(e.target.files[0]);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    handleFile(e.dataTransfer.files[0]);
  };

  

  return (
    <div
      className={`profile-container ${dragActive ? "drag-active" : ""}`}
      onDrop={handleDrop}
      onDragOver={(e) => {
        e.preventDefault();
        setDragActive(true);
      }}
      onDragLeave={() => setDragActive(false)}
    >
      <img
        src={image || "https://via.placeholder.com/150"}
        alt="Profile"
        className="profile-image"
      />

      {/* Progress Bar */}
      {uploading && (
        <div className="progress-circle">
            <svg className="progress-svg" viewBox="0 0 100 100">
                <circle
                    className="progress-bg"
                    cx="50"
                    cy="50"
                    r="45"
                />
                <circle
                    className="progress-indicator"
                    cx="50"
                    cy="50"
                    r="45"
                    style={{
                        strokeDashoffset: 282.6 - (282.6 * progress) / 100,
                    }}
                />
            </svg>

            <span className="progress-text">{progress}%</span>
        </div>
        )}

      <input
        type="file"
        accept="image/*"
        ref={fileRef}
        onChange={handleInputChange}
        hidden
      />
    </div>
  );
}


const uploadToServer = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const xhr = new XMLHttpRequest();

  xhr.upload.onprogress = (event) => {
    if (event.lengthComputable) {
      const percent = (event.loaded / event.total) * 100;
      setProgress(Math.round(percent));
    }
  };

  xhr.onload = () => {
    setUploading(false);
  };

  xhr.open("POST", "/upload");
  xhr.send(formData);

  setUploading(true);
};