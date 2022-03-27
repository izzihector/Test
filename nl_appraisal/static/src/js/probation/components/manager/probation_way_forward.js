ProbationWayForward = {
    inject: ['appraisalData', 'submitFunction', 'changeComponent', 'toggleChat'],
    data() {
        return {
            formData: {},
            disableButton: false,
            buttonText: "Save and next",
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
        changeReadOnlyMode(changeData=true) {
            this.readOnlyMode = !this.readOnlyMode
            if (this.readOnlyMode) {
                this.editButtonText = "Edit"
                this.toggleChat('block')
                if (changeData) this.writeDataToForm(this.appraisalData)
            }else {
                this.editButtonText = "Discard"
                this.toggleChat('none')
            }
        },
        writeDataToForm(data) {
            this.formData['appraisal_id'] = data.value['id']
            this.formData['has_sup_way_forward'] = true
            this.formData['p4_q1'] = data.value['p4_q1']
            this.formData['p4_q2'] = data.value['p4_q2']
        },
        async submitForm() {
            this.disableButton = true
            this.buttonText = "Saving..."
            if (this.formData.p4_q1 == 'yes') {
                this.formData.p4_q2 = null
            }
            result = await this.submitFunction(this.formData)
            if (result) {
                this.changeReadOnlyMode(changeData=false)
                if (this.appraisalData.value.metaInfo.setting_way_forward_state){
                    this.changeComponent('ProbationSubmitForm')
                }
            }
            this.disableButton = false
            this.buttonText = "Save and next"
        }
    },
    template: `
        <div>
            <h3 style="font-size: 20px;background: #ffffff;padding: 10px 0;margin-top: 20px;border-bottom: 4px solid #875a7b;text-transform: uppercase;">Way Forward</h3>
            <div class="py-5">
                <form class="form-group" @submit.prevent="submitForm">
                    <div class="form_buttons" v-if="appraisalData.value.metaInfo.hasCurrentComponentAccess">
                        <button type="button" class="btn btn-secondary text-white" @click="changeReadOnlyMode" v-if="!disableButton">{{ editButtonText }}</button>
                        <button  class="btn btn-secondary text-white" :disabled="disableButton" v-if="!readOnlyMode">{{ buttonText }}</button>
                    </div>
                    <label class="font-weight-normal mt-5 mr-4" for="">
                        Is the employee's employment with SCA confirmed?
                    </label>
                    <div class="custom-control custom-radio custom-control-inline">
                        <input type="radio" class="custom-control-input disabled-textarea" id="question1a" name="question1" value="yes" v-model="formData.p4_q1" :disabled="readOnlyMode">
                        <label class="custom-control-label" for="question1a">Yes</label>
                    </div>
                    <div class="custom-control custom-radio custom-control-inline">
                        <input type="radio" class="custom-control-input disabled-textarea" id="question1b" name="question1" value="no" v-model="formData.p4_q1" :disabled="readOnlyMode">
                        <label class="custom-control-label" for="question1b">No</label>
                    </div>

                    <label v-if="formData.p4_q1 != 'yes'" class="font-weight-normal mt-5" for="p4_q2">If no, give details of the performance concerns and the proposed way forward.</label>
                    <select v-if="formData.p4_q1 != 'yes'" :disabled="readOnlyMode" class="form-control disabled-textarea" v-model="formData.p4_q2" name="p4_q2" id="p4_q2">
                        <option value="termination">Termination of Contract</option>
                        <option value="improvement">Performance Improvement Plan</option>
                    </select>
            </form>
            </div>    
        </div>
    `,
}