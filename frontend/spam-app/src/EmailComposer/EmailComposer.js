import './EmailComposer.css'
import {useRef, useState} from 'react'

function EmailComposer(){

    const [isSpam, setIsSpam] = useState(false)
    const bodyRef = useRef(null)

    /**
     * Send the content of the email to the backend for spam detection
     */
    const handleSendEmail = () =>{
        
        const emailBody = bodyRef.current.value;
        const request = {
            method:'POST',
            mode:'cors',
            headers:{
                "Content-Type":'application/json'
            },
            body:JSON.stringify({
                content: emailBody
            })
        }

        console.log(request)

        fetch('http://127.0.0.1:8000/predict/', request).then((response) =>{
            console.log(response)
            return response.json()
        }).then((data) => {
            console.log(data)
            setIsSpam(data.classification === 1)
        }).catch((error) => {
            console.error('Error: ', error)
        })
    }

    return(
        <table className='email-composer'>
            <thead height="10%">
                <tr>
                    <td>
                        <div className='message-header'>
                            <span>New Message</span>
                            <div className={isSpam ? 'tab spam' : 'tab ham'}>
                                status: {isSpam ? 'SPAM' : 'HAM'}
                            </div>
                        </div>
                    </td>
                </tr>
            </thead>
            <tbody>
                <tr height="5%">
                    <td><input placeholder='To:' type="text"/></td>
                </tr>
                <tr height="5%">
                    <td><input placeholder='Subject:' type="text"/></td>
                </tr>
                <tr height="80%">
                    <td><textarea placeholder="Message" ref={bodyRef}></textarea></td>
                </tr>
                <tr>
                    <td><button onClick={handleSendEmail} >Send</button></td>
                </tr>
            </tbody>
            
        </table>
    )
}

export default EmailComposer