import './EmailComposer.css'
function EmailComposer(){

    return(
        <table className='email-composer'>
            <thead height="10%">
                <tr>
                    <td>New Message</td>
                </tr>
            </thead>
            <tbody>
                <tr height="5%">
                    <td><input placeholder='To:' type="text"/></td>
                </tr>
                <tr height="5%">
                    <td><input input placeholder='Subject:' type="text"/></td>
                </tr>
                <tr height="100%">
                    <textarea placeholder="Message">

                    </textarea>
                </tr>

            </tbody>
            <button>Send</button>
        </table>
    )
}

export default EmailComposer