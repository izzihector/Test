ESelfAssessment = {
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
          if (newVal.value) this.writeDataToForm(newVal);
        },
        immediate: true,
        deep: true,
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
            this.formData['has_emp_assessments_feed'] = true
            this.formData['p3_q1_emp_comments'] = data.value['p3_q1_emp_comments']
            this.formData['p3_q2_emp_comments'] = data.value['p3_q2_emp_comments']
            this.formData['p3_q3_emp_comments'] = data.value['p3_q3_emp_comments']
            this.formData['p3_q4_emp_comments'] = data.value['p3_q4_emp_comments']
        },
        async submitForm() {
            this.disableButton = true
            this.buttonText = "Saving..."
            result = await this.submitFunction(this.formData)
            if (result) {
                this.changeReadOnlyMode(changeData=false)
                if (this.appraisalData.value.metaInfo.employee_assessment_state){
                    this.changeComponent('ECareerAspiration')
                }
            }
            this.disableButton = false
            this.buttonText = "Save and next"
        }
  },
  template: `
        <div>
        <h4 style="font-size: 20px;background: #ffffff;padding: 10px 0;margin-top: 20px;border-bottom: 4px solid #875a7b;text-transform: uppercase;">Technical and behavioral competencies Assessment</h4>
        <div class="text-center">
        <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" data-name="Layer 1" width="250" height="200" viewBox="0 0 1080 639.01401"><path id="a513f258-927a-4de2-b47c-f6d8484aa7b1-486" data-name="Path 103" d="M345.467,477.129l-1.153-.26c31.95834-141.34216,172.44613-230.0153,313.78829-198.057A262.383,262.383,0,0,1,856,476.16893l-1.152.262c-27.208-119.463-131.908-202.9-254.612-202.9C479.14,273.536,371.994,359.159,345.467,477.129Z" transform="translate(-60 -130.493)" fill="#e6e6e6"/><path id="b48e35fb-0fa9-4a6e-a77a-d5ee8c8a325a-487" data-name="Path 104" d="M1140,744.493H60v-614H1140Zm-1078-2H1138v-610H62Z" transform="translate(-60 -130.493)" fill="#3f3d56"/><circle id="f75cebf4-07f7-4414-ab86-40e5ab2d2599" data-name="Ellipse 12" cx="74" cy="62.99997" r="9" fill="#875a7b"/><circle id="b3bbee1c-ff7e-4047-80a7-543833fb4a02" data-name="Ellipse 13" cx="101" cy="62.99997" r="9" fill="#f2f2f2"/><circle id="b056dc2b-10c3-4366-8b68-ab2b41800264" data-name="Ellipse 14" cx="128" cy="62.99997" r="9" fill="#f2f2f2"/><path id="b7f9e633-caf8-48cc-9bf3-ee1e6a98fd8b-488" data-name="Path 107" d="M1097,642.708v66.785h-71.119A86.746,86.746,0,0,1,1097,642.708Z" transform="translate(-60 -130.493)" fill="#e6e6e6"/><path id="afff29c9-505b-4418-a373-01de3d3be863-489" data-name="Path 108" d="M971.82,313.593l-.64-.77L731.79,511.353l-.77.64,165.87,200h2.6L733.84,512.253l237.08-196.61L1097,467.673v-3.14Z" transform="translate(-60 -130.493)" fill="#e6e6e6"/><circle id="f8cef931-c3bb-4037-9a50-1e0fdc7c5e4a" data-name="Ellipse 15" cx="704.53398" cy="222.81497" r="61.692" fill="#a0616a"/><path id="a345d496-be51-4ced-87e4-88917a587ade-490" data-name="Path 111" d="M867.08628,483.47072l-34.33043,99.53459v.0088l-16.54511,47.99052s-1.6888,76.30462-3.38641,76.30462c-.35186,0-.85318,1.09949-1.41613,2.83226H647.01246L660.20634,569.9522l-.80921-6.53187-10.32031-83.73087a41.96162,41.96162,0,0,1,27.72937-44.71969l17.24517-6.06274a136.52441,136.52441,0,0,1,70.5103-5.376l.00007,0A136.52428,136.52428,0,0,1,822.171,449.1842Z" transform="translate(-60 -130.493)" fill="#875a7b"/><path id="a678a244-be81-46d4-9955-cfd6d99b50a8-491" data-name="Path 113" d="M818.033,303.605S798.446,261.167,760.9,270.96s-58.761,24.484-60.393,39.174.816,36.726.816,36.726,4.081-30.2,30.2-23.668,66.922,1.632,66.922,1.632l6.529,58.761s7.345-10.61,15.506-4.081S844.149,316.663,818.033,303.605Z" transform="translate(-60 -130.493)" fill="#2f2e41"/><path id="b1de1415-f5bf-440f-a8b8-fa9f905c1360-492" data-name="Path 114" d="M899.30573,637.7863s0,38.746-14.24059,72.35521H836.13345l.431-1.13466L850.12778,649.652l-5.084-20.345-12.28786-46.29291v-.00884a135.32972,135.32972,0,0,1,1.08622-73.281l.5563-1.87088a34.10243,34.10243,0,0,1,32.68794-24.38265h0s22.04256,18.65613,20.345,54.262Z" transform="translate(-60 -130.493)" fill="#875a7b"/><path id="f1868812-8ac7-4b0c-a438-ab55a4a15b12-493" data-name="Path 121" d="M1040.387,252.532a33.376,33.376,0,1,1,33.376-33.376v0A33.376,33.376,0,0,1,1040.387,252.532Zm0-65.2a31.824,31.824,0,1,0,31.824,31.824h0A31.824,31.824,0,0,0,1040.387,187.332Z" transform="translate(-60 -130.493)" fill="#ccc"/><path id="b1b186d5-33ae-41a2-a01c-c43193f01a60-494" data-name="Path 123" d="M1097,711.993H103v-549h994Zm-992.159-1.788h990.31794V164.781H104.841Z" transform="translate(-60 -130.493)" fill="#ccc"/><path id="b98eb8ea-1fd7-4cba-9afb-7866ed7d6078-495" data-name="Path 122" d="M1054.448,206.463l-.729-.729-13.554,13.555-13.555-13.555-.729.729,13.554,13.554-11.75,11.75.729.729,11.75-11.75,11.75,11.75.729-.729-11.75-11.75Z" transform="translate(-60 -130.493)" fill="#3f3d56"/><path id="a9b170f1-abe6-494b-85b0-d8713abcdd5c-496" data-name="Path 146" d="M475.826,477.939H136.952A11.969,11.969,0,0,0,125,489.891V620.659a11.969,11.969,0,0,0,11.952,11.957H475.826a11.969,11.969,0,0,0,11.952-11.952V489.891A11.969,11.969,0,0,0,475.826,477.939Zm10.546,142.721a10.559,10.559,0,0,1-10.546,10.546H136.952a10.559,10.559,0,0,1-10.546-10.546V489.891a10.559,10.559,0,0,1,10.546-10.546H475.826a10.559,10.559,0,0,1,10.546,10.546Z" transform="translate(-60 -130.493)" fill="#3f3d56"/><path id="b6b39a3c-92e5-4d4e-830c-c9cb70ad8092-497" data-name="Path 141" d="M456.003,515.938H278.481c-5.156,0-9.39,3.4-9.591,7.686a2.14225,2.14225,0,0,0-.015.314c.007,4.416,4.3,7.994,9.606,8H456.003c5.305,0,9.606-3.582,9.606-8S461.309,515.938,456.003,515.938Z" transform="translate(-60 -130.493)" fill="#875a7b"/><path id="ae94418e-82bb-46b2-bcad-c3c282755a35-498" data-name="Path 141-2" d="M456.003,547.939H278.481c-5.156,0-9.39,3.4-9.591,7.686a2.14225,2.14225,0,0,0-.015.314c.007,4.416,4.3,7.994,9.606,8H456.003c5.305,0,9.606-3.582,9.606-8S461.308,547.939,456.003,547.939Z" transform="translate(-60 -130.493)" fill="#875a7b"/><path id="e8feddc1-03fc-4048-aa80-45fc0ee9652e-499" data-name="Path 141-3" d="M456.003,579.939H278.481c-5.156,0-9.39,3.4-9.591,7.686a2.14218,2.14218,0,0,0-.015.314c.007,4.416,4.3,7.994,9.606,8H456.003c5.305,0,9.606-3.582,9.606-8S461.309,579.939,456.003,579.939Z" transform="translate(-60 -130.493)" fill="#875a7b"/><path id="bcd0b27f-9e6f-4dd4-9c6b-301806d9c28e-500" data-name="Path 140" d="M194.988,597.938a42.353,42.353,0,1,1,42.353-42.353,42.353,42.353,0,0,1-42.353,42.353Zm0-83.245a40.892,40.892,0,1,0,40.892,40.892v0A40.892,40.892,0,0,0,194.988,514.693Z" transform="translate(-60 -130.493)" fill="#3f3d56"/><path id="a4b95a53-3e76-43d9-9905-f39259c2aa97-501" data-name="Path 118" d="M356,693.493H320v-36h36Zm-34-2h32v-32H322Z" transform="translate(-60 -130.493)" fill="#ff6584"/><path id="b5224a29-3e2c-47b8-aafd-f30a3a8a6089-502" data-name="Path 119" d="M277.185,682.018,264.324,670.23l1.352-1.474,11.139,10.212,25.353-38.03,1.664,1.11Z" transform="translate(-60 -130.493)" fill="#3f3d56"/><path id="b1af4244-ebcd-4e3e-9659-fd120ece41f1-503" data-name="Path 120" d="M290,666.493v25H258v-32h25v-2H256v36h36v-27Z" transform="translate(-60 -130.493)" fill="#e5e5e5"/><circle id="aed972d3-7bba-44b7-a5d2-fd1675eb4fbc" data-name="Ellipse 18" cx="119.5" cy="438.49997" r="23.5" fill="#875a7b"/><path d="M486.90131,749.583a18.72381,18.72381,0,0,1,22.93829-17.26685l35.47958-56.28978,14.26942,31.495-35.87967,48.6252a18.82532,18.82532,0,0,1-36.80762-6.56359Z" transform="translate(-60 -130.493)" fill="#a0616a"/><path id="b4b1ee8f-44c7-4e6a-b1f2-73ec029b7adc-504" data-name="Path 115" d="M672.1765,441.36135l-1.95763.34573c-21.9973,3.88482-40.64832,18.90469-48.35052,39.8725q-.3465.94328-.66484,1.89732l-13.56592,61.04365L514.37184,722.57363l28.83121,16.95586s79.69978-93.26574,89.874-125.48519l40.96711-78.78491a25.53212,25.53212,0,0,0,2.86057-12.76089l-3.07108-79.80044A1.41257,1.41257,0,0,0,672.1765,441.36135Z" transform="translate(-60 -130.493)" fill="#875a7b"/></svg>
        </div>
        <legend class="mb-3 page-hint"><p class="hint">
        This section will focus on how the employee has demonstrated and integrated their profesioanl/technical and behavioral competencies in their day to day work including integration of SCA policies and values.</p></legend>      
            <div class="py-1">
                <form class="form-group" @submit.prevent="submitForm">
                    <div class="form_buttons" v-if="appraisalData.value.metaInfo.hasCurrentComponentAccess">
                        <button type="button" class="btn btn-secondary text-white" @click="changeReadOnlyMode" v-if="!disableButton">{{ editButtonText }}</button>
                        <button  class="btn btn-secondary text-white" :disabled="disableButton" v-if="!readOnlyMode">{{ buttonText }}</button>
                    </div>
                    <div class="questions">
                        <span class="objective-title">Question 1.</span>
                        <p class="question-text">
                          How has the employee demonstrated their technical skills and competencies in the day-to-day work during the review period in terms of the professional skills, knowledge, accuracy of work, timelines and meeting deadlines and analysis of information for value addition to their work? Use specific examples where necessary
                        </p>
                        <span class="objective-title">Employee Answer</span>
                        <div class="question-feedback">
                          <textarea class="form-control question-feedback-textarea" rows="5" placeholder="Provide your comments here ......" :disabled="readOnlyMode" v-model="formData.p3_q1_emp_comments" name="p3_q1_emp_comments" id="p3_q1_emp_comments"></textarea>
                        </div>
                    </div>
                    <div class="questions">
                      <span class="objective-title">Question 2.</span>
                        <p class="question-text">
                        How has the employee demonstrated their skills and competencies working with others through communication, coordination, and collaboration as a member of the team, supervisor, or line manager with the unit/department? Please cite examples and incidents
                        </p>
                        <span class="objective-title">Employee Answer</span>
                        <div class="question-feedback">
                          <textarea class="form-control question-feedback-textarea" rows="5" placeholder="Provide your comments here ......" :disabled="readOnlyMode" v-model="formData.p3_q2_emp_comments" name="p3_q2_emp_comments" id="p3_q2_emp_comments"></textarea>
                        </div>
                    </div>
                   
                    <div class="questions">
                      <span class="objective-title">Question 3.</span>
                        <p class="question-text">
                        How has the employee proved their leadership ability to work independently, under pressure, leading through a crisis, adapting to changes  developing others through delegation and support?
                        </p>
                        <span class="objective-title">Employee Answer</span>
                        <div class="question-feedback">
                          <textarea class="form-control question-feedback-textarea" rows="5" placeholder="Provide your comments here ......" :disabled="readOnlyMode" v-model="formData.p3_q3_emp_comments" name="p3_q3_emp_comments" id="p3_q3_emp_comments"></textarea>
                        </div>
                    </div>
                 
                  <div class="questions">
                      <span class="objective-title">Question 4.</span>
                        <p class="question-text">
                        How has the employee integrated the SCA policies and values <strong>(responsiveness, equality, impartiality, social justice and integrity)</strong> in the day-to-day work during the review period. Key pointers include gender, diversity and inclusion (GDI), enforcing and reinforcing policies, relationship building and support to colleagues, field teams, partners and key stakeholders etc.) Please cite specific examples that demonstrated application and integration of the values. 
                        </p>
                        <span class="objective-title">Employee Answer</span>
                        <div class="question-feedback">
                          <textarea class="form-control question-feedback-textarea" rows="5" placeholder="Provide your comments here ......" :disabled="readOnlyMode" v-model="formData.p3_q4_emp_comments" name="p3_q4 _emp_comments" id="p3_q4 _emp_comments"></textarea>
                        </div>
                  </div>
                </form>
            </div>    
        </div>
    `,
};
