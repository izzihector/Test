ProbationStateReturner = {
    inject: ['appraisalData', 'submitFunction', 'changeComponent'],
    data() {
        return {
            formData: {sup_state_comment: '', state_returning:true},
            disableButton: false,
            buttonText: "Submit",
            readOnlyMode: true,
            editButtonText: "Edit"
        }
    },
    watch: {
        appraisalData: {
            handler(newVal, oldVal) {
                if (newVal.value) this.writeDataToForm(newVal)
            },
            immediate: true,
            deep: true
        },
    },
    methods: {
        writeDataToForm(data) {
            this.formData['appraisal_id'] = data.value['id']
        },
        async submitForm() {
            if(!confirm('Are you sure?')) {
                return
            }
            
            this.buttonText = 'Submiting...'
            this.disableButton = true
            await this.submitFunction(this.formData)
            this.disableButton = false
            this.buttonText = 'Submit'

        }
    },
    template: `
        <div>
            <h3 style="font-size: 20px;background: #ffffff;padding: 10px 0;margin-top: 20px;border-bottom: 4px solid #875a7b;text-transform: uppercase;">Move back to {{appraisalData.value.state == 'supervisor_assessment'? 'Self Assessment' : 'Supervisor Assessment'}} state.</h3>
            <div class="py-5">
                <form class="form-group" @submit.prevent="submitForm">
                    <label class="font-weight-normal mt-5" for="sup_state_comment">
                        Please briefly explain why are changing the appraisal record back.
                    </label>
                    <textarea class="form-control" rows="5" placeholder="Manager Comment..." 
                        v-model="formData.sup_state_comment" name="sup_state_comment" id="sup_state_comment"></textarea>
                    <br/>
                    <button class="btn btn-secondary bt-sm btn-odoo py-2" :disabled="disableButton">{{buttonText}}</button>
                </form>
            </div>    
        </div>
    `,
}